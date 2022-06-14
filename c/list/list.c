#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include "list.h"

//初始化双向链表
ListNode* ListInit(ListNode* phead)
{
    phead = BuyList(0);
    phead->next = phead;
    phead->prev = phead;
    return phead;
}

//双向链表打印
void ListPrint(ListNode* phead)
{
    ListNode* cur = phead->next;
    while (cur != phead)
    {
        printf("%d ", cur->val);
        cur = cur->next;
    }
    printf("\n");
}

// 创建返回链表的头结点
ListNode* BuyList(ListDateType x)
{
    ListNode* newnode = (ListNode*)malloc(sizeof(ListNode));
    if (newnode == NULL)
    {
        printf("BuyList fail\n");
        exit(-1);
    }
    newnode->val = x;
    newnode->next = NULL;
    newnode->prev = NULL;
    return newnode;
}

//双向链表尾插
ListNode* ListPushBack(ListNode* phead, ListDateType x)
{
    assert(phead);
    ListNode* newnode = BuyList(x);
    ListNode* tail = phead->prev;

    tail->next = newnode;
    phead->prev = newnode;
    newnode->next = phead;
    newnode->prev = tail;
    
    return newnode;
}

//双向链表尾删
void ListPopBack(ListNode* phead)
{
    assert(phead->next != phead);
    ListNode* tail = phead->prev;
    ListNode* prev = tail->prev;
    phead->prev = prev;
    prev->next = phead;
    free(tail);
    tail = NULL;
}

//双向链表头插
ListNode* ListPushFront(ListNode* phead, ListDateType x)
{
    assert(phead);
    ListNode* newnode = BuyList(x);
    ListNode* head = phead->next;

    phead->next = newnode;
    head->prev = newnode;
    newnode->next = head;
    newnode->prev = phead;
    
    return newnode;
}

//双向链表头删
void ListPopFront(ListNode* phead)
{
    assert(phead);
    assert(phead->next != phead);

    ListNode* head = phead->next;
    ListNode* next = head->next;

    phead->next = next;
    next->prev = phead;
    free(head);
    head = NULL;
}

//双向链表查找
ListNode* ListFind(ListNode* phead, ListDateType x)
{
    assert(phead);
    assert(phead->next != phead);
    ListNode* pos = phead->next;
    while (pos != phead)
    {
        if (pos->val == x)
        {
            return pos;
        }
        pos = pos->next;
    }
    return NULL;
}

//在pos之前插入
ListNode* ListInsert(ListNode* pos, ListDateType x)
{
    assert(pos);
    ListNode* newnode = BuyList(x);
    ListNode* prev = pos->prev;

    prev->next = newnode;
    pos->prev = newnode;
    newnode->prev = prev;
    newnode->next = pos;
    
    return newnode;
}

//删除pos位置
void ListErase(ListNode* pos)
{
    assert(pos);
    ListNode* prev = pos->prev;
    ListNode* next = pos->next;
    prev->next = next;
    next->prev = prev;
    free(pos);
    pos = NULL;
}

int main(int argc, const char *argv[])
{
    ListNode* phead = NULL;
    ListNode* pos = NULL;

    phead = ListInit(phead);
    ListPushBack(phead, 1);
    ListPushBack(phead, 2);
    ListPrint(phead);
    pos = ListFind(phead, 1);
    ListErase(pos);
    ListPrint(phead);
}