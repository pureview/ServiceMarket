/**
 * Created by funing on 2018/5/30.
 */

//在右侧打开tab选项
function openTab(title,id,url)
{
    // 对选择样式进行处理
    $("li").removeClass('background');
    $("#"+id).addClass('background');
    // 创建tab标签
    var content = '<iframe scrolling="auto" frameborder="0" data-options="closable:true"  src="'+url+'" style="width:100%;height:100%;"></iframe>';
    // 判断tab标签是否存在
    if ($("#tabs").tabs('exists', title))
    {
        $('#tabs').tabs('select', title);
    } else {
        $('#tabs').tabs('add', {
            title : title,
            closable : true,
            content : content
        });
    }
}