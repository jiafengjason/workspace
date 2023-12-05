package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"fmt"
)

func main() {
	key := []byte("CASB2021EnLink!!")
	iv := []byte("CASB2021EnLink!!")
	plaintext := []byte("192.168.108.16:8017")

	// 加密
	ciphertext, err := encrypt(plaintext, key, iv)
	if err != nil {
		fmt.Println("Encryption error:", err)
		return
	}

	fmt.Printf("Plaintext: %s\n", plaintext)
	fmt.Printf("Ciphertext: %x\n", ciphertext)

	// 解密
	decryptedText, err := decrypt(ciphertext, key, iv)
	if err != nil {
		fmt.Println("Decryption error:", err)
		return
	}

	fmt.Printf("Decrypted text: %s\n", decryptedText)
}

// 使用AES CBC方式加密
func encrypt(plaintext, key, iv []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	// 创建CBC加密器
	mode := cipher.NewCBCEncrypter(block, iv)

	// 进行PKCS5Padding填充
	paddedText := pkcs5Padding(plaintext, aes.BlockSize)

	// 加密密文
	ciphertext := make([]byte, len(paddedText))
	mode.CryptBlocks(ciphertext, paddedText)

	return ciphertext, nil
}

// 使用AES CBC方式解密
func decrypt(ciphertext, key, iv[]byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	// 创建CBC解密器
	mode := cipher.NewCBCDecrypter(block, iv)

	// 解密密文
	paddedText := make([]byte, len(ciphertext))
	mode.CryptBlocks(paddedText, ciphertext)

	// 进行PKCS5Padding填充还原
	originalText := pkcs5UnPadding(paddedText, aes.BlockSize)

	return originalText, nil
}

// PKCS5Padding填充
func pkcs5Padding(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	return append(data, padText...)
}

// PKCS5UnPadding去除填充
func pkcs5UnPadding(data []byte, blockSize int) []byte {
	length := len(data)
	unpadding := int(data[length-1])
	return data[:(length - unpadding)]
}



