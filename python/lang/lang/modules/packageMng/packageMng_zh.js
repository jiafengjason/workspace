/*
 * @Author:  liff liff@enlink.cn
 * @Date: 2023-05-30 20:10:19
 * @LastEditors: liff liff@enlink.cn
 * @LastEditTime: 2023-06-09 10:33:35
 * @FilePath: \ensbrain-web-admin\src\i18n\lang\modules\packageMng\packageMng_zh.js
 * @Description: 
 * 
 * Copyright (c) 2017-2023 . Jiangsu Enlink Network Technology Co.,Ltd., All Rights Reserved. 
 */
export const packageMng_zh = {
  pkgRelease: {
    title: '版本管理',
    clientSide: '客户端',
    downloadCenterConfig: '下载中心配置',
    baseInputPlaceholder: '组件名称',
    deleteComponent: '删除组件',
    userLabel: '用户',
    deviceLabel: '设备',
    frequencyTip: '一分钟可以升级的客户端次数（次/min）',
    speedTip: '控制客户端下载速率（kb/s）',
    numberTip: '请输入{number}正整数',
  },
  toolsAndFiles: {
    title: '工具和文件',
    toolName: '工具名称',
    deleteTools: '删除工具',
    normal: '正常',
    abnormal: '异常',
    fileName: '文件名称',
    deleteFile: '删除文件',
    fileTypeTip: '只能上传doc、docx或pdf格式的文件',
  },
  dispatchCenter: {
    title: '分发中心',
    dispatchCenterDesc: '通过下载中心，分发客户端、相关工具和文件，用户使用浏览器访问下载。',
    dynamicUrl: '动态下载链接',
    validDays: '链接有效期',
    day: '天',
    dayNumber: '(1-100天)',
    emailContent: '邮件内容',
    preview: '预览',
    emailContentTip: '请输入邮件内容',
    sendObject: '发送对象',
    sendEmail: '发送邮件',
    sendConfirmTip: '用户可以通过链接访问下载中心，当前选中用户{total}人，其中有 {emailBind}人邮箱绑定，是否确认发送？',
    spaCloseTip: '请确保SPA已关闭，否则链接无法使用!',
    downloadServer: '下载中心服务器',
    inputServerTip: '请输入下载中心服务器',
    fileDownloadUrl: '文件下载地址',
    inputFileServerTip: '请输入文件下载地址',
    dynamicMode: '启用动态控制',
    downloadFrequencyTip: '每分钟的最大下载次数（次/min）',
    fileDownloadRateTip: '文件下载速率（KB/s）',
    frequencyRate: '次/min',
    emailText: '尊敬的用户:管理员邀请你使用客户端，下载链接为：url，有效期至time。系统邮件无需回复。',
    sendSuccess: '发送成功！',
    sendErrorTip: '您要发送的邮件内容未包含有效的下载链接，请检查相关配置！',
    configSuccess: '配置成功！',
    copyTip: '链接已复制到粘贴板',
    copyErrorTip: '当前链接不支持复制黏贴',
  },
}
