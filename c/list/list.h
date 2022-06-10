// 2、带头+双向+循环链表增删查改实现
typedef int ListDateType;
typedef struct ListNode 
{
    ListDateType val;
    struct ListNode* prev;
    struct ListNode* next;
}ListNode;
 
//初始化双向链表
ListNode* ListInit(ListNode* phead);
//双向链表打印
void ListPrint(ListNode* phead);
// 创建返回链表的头结点.
ListNode* BuyList(ListDateType x);
//双向链表尾插
void ListPushBack(ListNode* phead,ListDateType x);
//双向链表尾删
void ListPopBack(ListNode* phead);
//双向链表头插
void ListPushFront(ListNode* phead, ListDateType x);
//双向链表头删
void ListPopFront(ListNode* phead);
//双向链表查找
ListNode* ListFind(ListNode* pHead, ListDateType x);
//在pos之前插入
void ListInsert(ListNode* pos, ListDateType x);
//删除pos位置
void ListErase(ListNode* pos);