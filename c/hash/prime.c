#include <stdio.h>
#include <stdlib.h>
 
#define N 13
#define ADDR_SIZE 8
 
//hash表的链表的节点
typedef struct node {
    int data;//存数据
    struct node *next;//存指针
}HASH;
 
//创建hash表
HASH **create_hash()
{
    HASH **h = (HASH **)malloc(N * ADDR_SIZE);
    int i = 0;
    for (i = 0; i < N; i++)
    {
        h[i] = (struct node *)malloc(sizeof(struct node));
        h[i]->next = NULL;
    }
    return h;
}
 
//插入数据
int insert_hash_table(HASH **h, int data)
{
    int key = data % N; 
    struct node * p = h[key];
    //头插法插入数据
    struct node * temp;
    temp = (struct node *)malloc(sizeof(struct node));
    temp->data = data;
    temp->next = p->next;
    p->next = temp;

    return 0;
}
 
//遍历
int show_hash_table(struct node *head)
{
    //如果链表后面没有数据，则用---0---表示链表存在但是没有数据
    if (head->next == NULL)
    {
        puts("---0---");
        return -1;
    }

    //遍历链表，打印数据
    while(head->next != NULL)
    {
        head = head->next;
        printf("%d ", head->data);
    }
    putchar(10);
    return 0;
}
 
//释放链表节点
int free_hash_table(struct node *head)
{
    //如果链表后面没有数据，则无需释放
    if (head->next == NULL)
    {
        return 0;
    }

    //遍历这个链表-头删法释放
    while(head->next != NULL)
    {
        //定义一个结构体指针变量 来指向这个即将被删除的结构体 以便释放        
        struct node *temp = head->next;
        head->next = head->next->next;
        printf("--%d--将被释放\n",temp->data);
        free(temp);
        temp = NULL;
    }
    return 0;
}
 
//查找数据
int search_hash_table(HASH **h, int data)
{
    int key = data % N; //数据对质数取余，得到键值
    struct node *p = h[key]; //找到对应链表

    //对比要查找的数据
    while (p->next != NULL )
    {
        if (p->next->data == data)
        {
            return 1;//找到返回1
        }
        p = p->next;
    }
    //没有找到返回0
    return 0;
}

//11个数据，那么m : n/0.75 = 14， 最大质数为13
int main(int argc, const char *argv[])
{
    int a[11] = {100, 34, 14, 45, 46, 98, 68, 69, 7, 31, 26};
 
    //创建hash表
    HASH **h = create_hash();
    int i = 0;
    int num = 0;
    for (i = 0; i < 11; i++)
    {
        insert_hash_table(h, a[i]);//链表的插入
    }
    //打印hash表--无实际意义
    printf("-------这是hash表--------------------\n");
    for (i = 0; i < N; i++)
    {
        show_hash_table(h[i]);//链表的遍历
    }
    printf("--------hash表结束--------------------\n");
    printf("数组数据如下-->用于测试，无实质意义,遍历HASH表也是<---\n");
    for(i = 0;i < 11;i ++)
    {
        printf("%d  ",a[i]);	
    }
    putchar(10);

    printf("please input need 查找 de number >>");
    scanf("%d",&num);
 
    //--查找--
    if(search_hash_table(h, num) == 1)
    {
        printf("---data %d is exists---\n", num); 
    }
    else
    {
        printf("---data %d is not exists---\n", num);
    }
 
    //链表的释放
    for(i = 0;i < 11;i ++)
    {
        free_hash_table(h[i]);
    }
    printf("---链表释放完成---\n");
    free(h);
    printf("---指针数组释放---\n");
    return 0;
}