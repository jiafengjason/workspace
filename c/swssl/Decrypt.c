#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include "swsds.h"

#define BUFFER_SIZE 1024
/*
typedef struct ECCCipher_Internal_st
{
    unsigned int clength;
    unsigned char x[ECCref_MAX_LEN_INTERNAL];
    unsigned char y[ECCref_MAX_LEN_INTERNAL];
    unsigned char C[ECCref_MAX_CIPHER_LEN_INTERNAL];
    unsigned char M[ECCref_MAX_LEN_INTERNAL];
} ECCCipher_Internal;
*/
int PrintData(char *itemName, unsigned char *sourceData, unsigned int dataLength, unsigned int rowCount)
{
    int i, j;

    if((sourceData == NULL) || (rowCount == 0) || (dataLength == 0))
        return -1;

    if(itemName != NULL)
        printf("%s[%d]:\n", itemName, dataLength);

    for(i=0; i<(int)(dataLength/rowCount); i++)
    {
        printf("%08x  ",i * rowCount);

        for(j=0; j<(int)rowCount; j++)
        {
            printf("%02x ", *(sourceData + i*rowCount + j));
        }

        printf("\n");
    }

    if (!(dataLength % rowCount))
        return 0;

    printf("%08x  ", (dataLength/rowCount) * rowCount);

    for(j=0; j<(int)(dataLength%rowCount); j++)
    {
        printf("%02x ",*(sourceData + (dataLength/rowCount)*rowCount + j));
    }

    printf("\n");

    return 0;
}

void printECCCipher(ECCCipher *cipher) {
    printf("x: ");
    for (int i = 0; i < ECCref_MAX_LEN; i++) {
        printf("%02X", cipher->x[i]);
    }
    printf("\ny: ");
    for (int i = 0; i < ECCref_MAX_LEN; i++) {
        printf("%02X", cipher->y[i]);
    }
    printf("\nM: ");
    for (int i = 0; i < 32; i++) {
        printf("%02X", cipher->M[i]);
    }
    printf("\nL: %u\n", cipher->L);
    printf("C: ");
    for (int i = 0; i < cipher->L; i++) {
        printf("%02X", cipher->C[i]);
    }
    printf("\n");
}
/*
SGD_RV ConvertECCCipherData_InternalToSt(ECCCipher *pCipherDataDest, ECCCipher_Internal *pCipherDataSrc)
{
    memset(pCipherDataDest->x, 0, ECCref_MAX_LEN * 2);

    memcpy(&pCipherDataDest->x[ECCref_MAX_LEN_INTERNAL], pCipherDataSrc->x, ECCref_MAX_LEN_INTERNAL);
    memcpy(&pCipherDataDest->y[ECCref_MAX_LEN_INTERNAL], pCipherDataSrc->y, ECCref_MAX_LEN_INTERNAL);
    memcpy(pCipherDataDest->M, pCipherDataSrc->M, ECCref_MAX_LEN_INTERNAL);
    pCipherDataDest->L = pCipherDataSrc->clength;
    memcpy(pCipherDataDest->C, pCipherDataSrc->C, pCipherDataSrc->clength);

    return SDR_OK;
}
*/
int main() {
    int rv = 0;
    SGD_HANDLE hDeviceHandle;
    SGD_HANDLE hSessionHandle;
    FILE *file;
    unsigned char inData[512], outData[512], tmpData[ECCref_MAX_CIPHER_LEN];
    int uiDataLength = 0;
    unsigned int outDataLen = 0;
    unsigned int len = 0;
    size_t bytesRead = 0;
    unsigned char data[512] = {0};
    ECCCipher *cipher = (ECCCipher *)data;
    //ECCCipher_Internal cipherDataSrc;

    //连接设备
    rv = SDF_OpenDevice(&hDeviceHandle);
    if (rv != SDR_OK)
    {
        printf("打开设备错误，错误码[0x%08x]\n", rv);
        return rv;
    }

    rv = SDF_OpenSession(hDeviceHandle, &hSessionHandle);
    if(rv != SDR_OK)
    {
        SDF_CloseDevice(hDeviceHandle);
        printf("打开会话句柄错误，错误码[0x%08x]\n", rv);
        return rv;
    }
    
    file = fopen("SE.key", "r");
    if (file == NULL) {
        printf("Failed to open file %s\n", strerror(errno));
        return rv;
    }
    
    while ((bytesRead = fread(inData, 1, BUFFER_SIZE, file)) > 0) {
        uiDataLength += bytesRead;
    }
    fclose(file);
    
    printf("inData:\n");
    for (int i=0;i<uiDataLength;i++) {
        printf("%x ", inData[i]);
    }
    printf("\n");
    
    memset(tmpData, 0, sizeof(tmpData));
    rv = SDF_InternalEncrypt_ECC(hSessionHandle, 1, SGD_SM2_3, inData, uiDataLength, (ECCCipher *)tmpData);
    if(rv != SDR_OK)
    {
        printf("公钥运算错误，错误码[0x%08x]\n", rv);
    }
    else
    {
        printf("加密数据:\n");
        printECCCipher((ECCCipher *)tmpData);
    }
    
    printf("tmpData:\n");
    for (int i=0;i<ECCref_MAX_CIPHER_LEN;i++) {
        printf("%x ", tmpData[i]);
    }
    printf("\n");
    //ConvertECCCipherData_InternalToSt(tmpData, &cipherDataSrc);

    /**/
    file = fopen("SE_Encrypt.key", "w");
    if (file == NULL) {
        printf("Error opening SE_Encrypt.key");
        return rv;
    }
    //fwrite((char *)&cipherDataSrc, 1, sizeof(cipherDataSrc), file);
    fclose(file);
    
    memset(tmpData, 0, sizeof(tmpData));
    file = fopen("encrypted.bin", "r");
    if (file == NULL) {
        printf("Failed to open file %s\n", strerror(errno));
        return rv;
    }
    
    while ((bytesRead = fread(tmpData, 1, BUFFER_SIZE, file)) > 0) {
        len += bytesRead;
    }
    printf("加密数据encrypted.bin:\n");
    printECCCipher((ECCCipher *)tmpData);

    memcpy(cipher->x + 32, tmpData, 32);
    memcpy(cipher->y + 32, tmpData + 32, 32);
    memcpy(cipher->M, tmpData + 2 * 32, 32);
    cipher->L = *(int *)(tmpData + 2 * 32 + 32);
    printf("cipher->L:%d len:%d ECCref_MAX_LEN:%d\n", cipher->L, len, ECCref_MAX_LEN);
    memcpy(cipher->C, tmpData + 2 * 32 + 32 + sizeof(cipher->L), len - (2 * 32 + 32 + sizeof(cipher->L)));
    fclose(file);

    rv = SDF_InternalDecrypt_ECC(hSessionHandle, 1, SGD_SM2_3, cipher, outData, &outDataLen);
    if(rv != SDR_OK)
    {
        printf("私钥运算错误，错误码[0x%08x]\n", rv);
        return rv;
    }
    else
    {
        printf("私钥运算成功。\n");
        PrintData("私钥运算结果", outData, outDataLen, 16);
    }

    file = fopen("SE_Decrypt.key", "w");
    if (file == NULL) {
        printf("Error opening SE_Decrypt.key");
        return rv;
    }
    fprintf(file, (char *)outData);
    fclose(file);

    return 0;
}
