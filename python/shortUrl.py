import pyshorteners as psn

#s = psn.Shortener(api_key="YOUR_KEY")
s = psn.Shortener()
long_url =input("Enter the URL to shorten: ")
#short_url = s.bitly.short(long_url)
short_url = s.clckru.short(long_url)
print("The shortened URL is: "+ short_url)
