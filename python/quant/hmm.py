# pip install yfinance hmmlearn pandas numpy matplotlib
import os
import numpy as np, pandas as pd, warnings, matplotlib.pyplot as plt, yfinance as yf
from hmmlearn import hmm

# 将 HTTPS 代理改为 HTTP 代理
proxy_address = "http://192.168.74.10:9910"  # 确保使用 http:// 而不是 https://

# 设置环境变量
os.environ['HTTP_PROXY'] = proxy_address
os.environ['HTTPS_PROXY'] = proxy_address

RANDOM_STATE = 42
asset, vix_sym, rate_sym = "SPY", "^VIX", "^TNX"
start, end = "2024-01-01", "2024-12-31"
n_states, min_len, stickiness = 4, 10, 10.0

def dl_close(sym, start, end):
    try:
        df = yf.download(sym, start=start, end=end, period="1d", progress=True)
        if isinstance(df.columns, pd.MultiIndex):
            s = df["Close"].droplevel(1, axis=1).squeeze().rename(sym)
        else:
            s = df["Close"].rename(sym)
        return s
    except Exception as e:
        print(f"下载 {sym} 失败: {e}")
        return pd.Series([], name=sym)

px = dl_close(asset, start, end)
vix = dl_close(vix_sym, start, end)
tnx = dl_close(rate_sym, start, end)
df = pd.concat([px, vix, tnx], axis=1).dropna()
df.columns = ["PX", "VIX", "TNX"]

lr = np.log(df["PX"]).diff().fillna(0.0)
vol = lr.rolling(20, min_periods=1).std()
ma50 = df["PX"].rolling(50).mean()
ma200= df["PX"].rolling(200).mean()
spread = ((ma50 - ma200) / ma200).fillna(0.0)
vix_n = df["VIX"].fillna(method="ffill")
rate = (df["TNX"] / 10.0).fillna(method="ffill")

X = np.column_stack([lr.values, vol.values, vix_n.values, spread.values, rate.values])
X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
Xm = (X - X.mean(axis=0, keepdims=True)) / (X.std(axis=0, keepdims=True) + 1e-12)

class HMMRegimeDetector:
    def __init__(self, n_states=4, covariance_type="diag", n_iter=300, tol=1e-4, random_state=None):
        self.model = hmm.GaussianHMM(n_components=n_states, covariance_type=covariance_type,
            n_iter=n_iter, tol=tol, random_state=random_state)
        self.n_states = n_states
    @staticmethod
    def enforce_min_duration(labels, min_len=10):
        s = np.array(labels, copy=True); n = len(s); i = 0
        while i < n:
            j = i + 1
            while j < n and s[j] == s[i]: j += 1
            if (j - i) < min_len:
                left = s[i-1] if i > 0 else None
                right = s[j] if j < n else None
                if left is None and right is not None: 
                    s[i:j] = right
                elif right is None and left is not None: 
                    s[i:j] = left
                elif left is not None and right is not None:
                    L = i-1
                    while L-1 >= 0 and s[L-1] == left: 
                        L -= 1
                        left_len = i - L
                        R = j
                    while R+1 < n and s[R+1] == right: R += 1
                    right_len = R - j + 1
                    s[i:j] = left if left_len >= right_len else right
            i = j
        return s
    def fit(self, X):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            self.model.fit(X)
        return self
    def make_sticky(self, strength=10.0):
        A = self.model.transmat_
        A = A + strength * np.eye(self.n_states)
        self.model.transmat_ = A / A.sum(axis=1, keepdims=True)
        return self
    def predict(self, X, min_len=10, sticky_strength=None):
        if sticky_strength is not None:
            self.make_sticky(sticky_strength)
        states = self.model.predict(X)
        states = self.enforce_min_duration(states, min_len=min_len)
        proba = self.model.predict_proba(X)
        return states, proba

detector = HMMRegimeDetector(n_states=n_states).fit(Xm)
states, proba = detector.predict(Xm, min_len=min_len, sticky_strength=stickiness)
out = df.copy()
out["log_ret"] = lr
out["state"] = states
state_means = out.groupby("state")["log_ret"].mean().sort_values(ascending=False)
ranked = state_means.index.tolist()
labels = {ranked[0]: "Bull", ranked[-1]: "Bear"}
for s in set(range(n_states)) - set(labels): labels[s] = "Neutral"
out["regime"] = out["state"].map(labels)
print("各状态日均对数收益率:\n", state_means, "\n")
print(out[["PX", "regime"]].tail())

fig, ax = plt.subplots(figsize=(10, 5), dpi=110)
ax.plot(out.index, out["PX"], label=asset)
colors = {"Bull":"#2ca02c", "Bear":"#d62728", "Neutral":"#1f77b4"}
prev = None
for i, (t, reg) in enumerate(out["regime"].items()):
    if i == 0 or reg != prev:
        if i: ax.axvspan(start_t, t, color=colors[prev], alpha=0.08)
        start_t, prev = t, reg
ax.axvspan(start_t, out.index[-1], color=colors[prev], alpha=0.08)
ax.set_title(f"{asset}: HMM 市场状态 (对数收益率, 20日波动率, VIX, MA50-200 差, 10年收益率)")
ax.legend(loc="upper left"); ax.grid(True, alpha=0.3)
plt.tight_layout(); plt.show()

out["position"] = 0
out.loc[out["regime"]=="Bull","position"] = 1
out.loc[out["regime"]=="Bear","position"] = -1
out["position"] = out["position"].shift(1).fillna(0)
out["strat_lr"] = out["position"] * out["log_ret"]
cum = np.exp(out[["log_ret","strat_lr"]].cumsum())
cum.columns = ["BuyHold", "HMM_Strategy"]

def sharpe(x, periods=252):
    mu, sd = x.mean(), x.std()
    return (mu/sd)*np.sqrt(periods) if sd>0 else np.nan
def max_drawdown(series):
    rollmax = series.cummax()
    return (series/rollmax - 1.0).min()

bh_cagr = cum["BuyHold"].iloc[-1]**(252/len(out)) - 1
st_cagr = cum["HMM_Strategy"].iloc[-1]**(252/len(out)) - 1
bh_sharp = sharpe(out["log_ret"])
st_sharp = sharpe(out["strat_lr"])
bh_mdd = max_drawdown(cum["BuyHold"])
st_mdd = max_drawdown(cum["HMM_Strategy"])
print(f"\n买入持有: CAGR={bh_cagr:.2%} Sharpe={bh_sharp:.2f} MaxDD={bh_mdd:.2%}")
print(f"HMM 策略: CAGR={st_cagr:.2%} Sharpe={st_sharp:.2f} MaxDD={st_mdd:.2%}")

fig, ax = plt.subplots(figsize=(9,4), dpi=110)
ax.plot(cum.index, cum["BuyHold"], label="买入持有")
ax.plot(cum.index, cum["HMM_Strategy"], label="HMM 策略")
ax.set_title("累积增长（基于对数收益率）")
ax.grid(True, alpha=0.3); ax.legend(); plt.tight_layout(); plt.show()