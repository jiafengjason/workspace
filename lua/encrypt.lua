local resty_random = require "resty.random"
local resty_sha1 = require "resty.sha1"
local resty_sha224 = require "resty.sha224"
local resty_sha256 = require "resty.sha256"
local resty_sha384 = require "resty.sha384"
local resty_sha512 = require "resty.sha512"
local resty_md5 = require "resty.md5"
local resty_aes = require "resty.aes"
local resty_des = require 'resty.des'
local resty_str = require "resty.string"
local resty_rsa = require "resty.rsa"

local nettle_padding = require "resty.nettle.padding"
local nettle_rsa = require "resty.nettle.rsa"

--[[
ngx.log(ngx.ERR,encrypt.random_char(16))
ngx.log(ngx.ERR,encrypt.random_hex(16))
ngx.log(ngx.ERR,encrypt.base64("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.sha1("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.sha224("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.sha256("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.sha384("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.sha512("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.md5("Enlink@123456"))
ngx.log(ngx.ERR,encrypt.aes("Enlink@123456","ANKKIUSEAESLOGIN",128,"ecb"))
ngx.log(ngx.ERR,encrypt.aes("Enlink@123456","ANKKIUSEAESLOGIN",128,"cbc","ANKKIUSEAESLOGIN"))
--not support 192 and 256
--ngx.log(ngx.ERR,encrypt.aes("Enlink@123456","ANKKIUSEAESLOGINABCDEFGH",192,"cbc","ANKKIUSEAESLOGINABCDEFGH")) 
--ngx.log(ngx.ERR,encrypt.aes("Enlink@123456","ANKKIUSEAESLOGINABCDEFGHIJKLMNOP",256,"cbc","ANKKIUSEAESLOGINABCDEFGHIJKLMNOP"))
ngx.log(ngx.ERR,encrypt.des("Enlink@123456","ANKKIUSE","ecb"))
ngx.log(ngx.ERR,encrypt.des("Enlink@123456","ANKKIUSE","cbc","ANKKIUSE"))
--ngx.log(ngx.ERR,encrypt.naes("Enlink@123456","ANKKIUSEAESLOGINABCDEFGH","cbc","ANKKIUSEAESLOGINABCDEFGH"))
--ngx.log(ngx.ERR,encrypt.naes("Enlink@123456","ANKKIUSEAESLOGINABCDEFGHIJKLMNOP","cbc","ANKKIUSEAESLOGINABCDEFGHIJKLMNOP"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSE","ecb"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSE","cbc","ANKKIUSE"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSE","ecb",nil,"pkcs7"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSE","cbc","ANKKIUSE","pkcs7"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSEABCDEFGHIJKLMNOP","ecb"))
ngx.log(ngx.ERR,encrypt.ndes("Enlink@123456","ANKKIUSEABCDEFGHIJKLMNOP","cbc","ANKKIUSE"))
--]]

local _M = {}

_M.enableNettle = false
math.randomseed(os.time())

function _M.timestamp(unit) 
    if unit=='s' then
        return os.time()
    elseif unit=='ms' then
        return 1000*os.time()
    end
end

function _M.randint(length)
    local t = {
        "0","1","2","3","4","5","6","7","8","9",
    }    
    local s = ""
    for i =1, length do
        s = s .. t[math.random(#t)]
    end
    return s
end

function _M.randchar(length)
    local t = {
        "0","1","2","3","4","5","6","7","8","9",
        "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
        "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
    }    
    local s = ""
    for i =1, length do
        s = s .. t[math.random(#t)]
    end
    return s
end

function _M.randhex(length)
    local rand = resty_random.bytes(length)
    return resty_str.to_hex(rand)
end

function _M.base64(plaintext)
    return ngx.encode_base64(plaintext)
end

function _M.sha1(plaintext)
    local sha1 = resty_sha1:new()
    if not sha1 then
        ngx.log(ngx.ERR, "failed to create the sha1 object")
        return
    end
    
    local ok = sha1:update(plaintext)
    if not ok then
        ngx.log(ngx.ERR, "failed to add data")
        return
    end

    local digest = sha1:final()  -- binary digest
    return resty_str.to_hex(digest)
end

function _M.sha224(plaintext)
    local sha224 = resty_sha224:new()
    sha224:update(plaintext)
    local digest = sha224:final()
    return resty_str.to_hex(digest)
end

function _M.sha256(plaintext)
    local sha256 = resty_sha256:new()
    sha256:update(plaintext)
    local digest = sha256:final()
    return resty_str.to_hex(digest)
end

function _M.sha384(plaintext)
    local sha384 = resty_sha384:new()
    sha384:update(plaintext)
    local digest = sha384:final()
    return resty_str.to_hex(digest)
end

function _M.sha512(plaintext)
    local sha512 = resty_sha512:new()
    sha512:update(plaintext)
    local digest = sha512:final()
    return resty_str.to_hex(digest)
end

function _M.md5(plaintext)
    local md5 = resty_md5:new()
    if not md5 then
        ngx.log(ngx.ERR, "failed to create md5 object")
        return
    end

    local ok = md5:update(plaintext)
    if not ok then
        ngx.log(ngx.ERR, "failed to add data")
        return
    end

    local digest = md5:final()
    return resty_str.to_hex(digest)
end

function _M.aes(plaintext, key, keyLength, mode, IV, padding)
    padding = padding or "nopadding"
    plaintext = nettle_padding[padding].pad(plaintext)
	print(plaintext)
	
    local aesMod
    local err
    if mode=="ecb" then
        IV = key
    end
    aesMod,err = resty_aes:new(key, nil, resty_aes.cipher(keyLength, mode), {iv = IV})
    if not aesMod then
        ngx.log(ngx.ERR, err)
        return
    end
    local ciphertext = aesMod:encrypt(plaintext)
    --ngx.log(ngx.ERR, "encrypted:"..ngx.encode_base64(encrypted))
    --ngx.log(ngx.ERR, "encrypted:"..encodeBase64(encrypted))
	print(ciphertext)
	print("\n")
    return ngx.encode_base64(ciphertext)
end

function _M.aesDec(plaintext, key, keyLength, mode, IV, padding)
    padding = padding or "nopadding"
    --plaintext = nettle_padding[padding].pad(plaintext)

    local aesMod
    local err
    if mode=="ecb" then
        IV = key
    end
	
    aesMod,err = resty_aes:new(key, nil, resty_aes.cipher(keyLength, mode), {iv = IV})
    if not aesMod then
        ngx.log(ngx.ERR, err)
        return
    end

	local cipherBytes = ngx.decode_base64(plaintext)
	if not cipherBytes then
		ngx.log(ngx.ERR, "decode base64 [" .. plaintext .. "] failed")
		return
	end

    local ciphertext = aesMod:decrypt(cipherBytes)
    return ciphertext
end

function _M.formatPublicKey(text)
	local key = "-----BEGIN PUBLIC KEY-----\n"
	for i=1,math.ceil(#text/64) do
		local s = i*64-63
		local e = i*64
		if s > #text then
			break
		end
		if e > #text then
			e = #text
		end
		key = key .. string.sub(text,s,e) .. "\n"
	end
	key = key .. "-----END PUBLIC KEY-----"
			
	return key
end

function _M.rsa(rsa_public_key, plain)
    local pub, err = resty_rsa:new({ public_key = rsa_public_key })
    if not pub then
        ngx.log(ngx.ERR, "new rsa err: ", err)
        return nil
    end

    local ciphertext, err = pub:encrypt(plain)
    if not ciphertext then
        ngx.log(ngx.ERR, "failed to encrypt: ", err)
        return nil
    end

	return ngx.encode_base64(ciphertext)
end

function _M.des(plaintext, key, mode, IV, padding)
    padding = padding or "nopadding"
    plaintext = nettle_padding[padding].pad(plaintext)

    local desMod
    local err
    if mode=="ecb" then
        IV = key
    end
    desMod,err =resty_des:new(key,nil, resty_des.cipher(mode), {iv = IV})

    if not desMod then
        ngx.log(ngx.ERR, err)
        return
    end

    local ciphertext = desMod:encrypt(plaintext)
    return ngx.encode_base64(ciphertext)
end

local ok, nettle_aes = pcall(require, "resty.nettle.aes")
if ok then
    local nettle_des = require "resty.nettle.des"
    _M.enableNettle = true

    function _M.naes(plaintext, key, mode, iv, padding)
        padding = padding or "nopadding"
        plaintext = nettle_padding[padding].pad(plaintext)

        local aesMod,err = nettle_aes.new(key, mode, iv)

        if not aesMod then
            ngx.log(ngx.ERR, err)
            return
        end

        local ciphertext = aesMod:encrypt(plaintext)
        return ngx.encode_base64(ciphertext)
    end

    function _M.ndes(plaintext, key, mode, iv, padding)
        padding = padding or "nopadding"
        plaintext = nettle_padding[padding].pad(plaintext)

        local desMod,err = nettle_des.new(key, mode, iv)

        if not desMod then
            ngx.log(ngx.ERR, err)
            return
        end

        local ciphertext = desMod:encrypt(plaintext)
        return ngx.encode_base64(ciphertext)
    end
end

return _M
