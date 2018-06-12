/**
 * Created by funing on 2018/6/1.
 */
$(function(){
    $("#manageApprentice_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : true,
        fitColumns:true,
        singleSelect:false,
        onClickCell: onClickCell,
        pageList : [ 5, 10, 15, 20 ],
        idField : 'id',
        columns:[
            [{
                field: 'id',
                title: '用户ID',
                align: 'center'
            },
            {
                field: 'master_id',
                title: '师父ID',
                align: 'center'
            },
            {
                field: 'age',
                title: '年龄',
                align: 'center'
            },
            {
                field: 'gender',
                title: '性别',
                align: 'center'
            },
            {
                field: 'create_date',
                title: '注册时间',
                align: 'center'
            },
            {
                field: 'wangwang',
                title: '旺旺号',
                align: 'center'
            },
            {
                field: 'wechat_id',
                title: '微信号',
                align: 'center'
            },
            {
                field: 'blacklist',
                title: '状态',
                align: 'center'
            },
            {
                field: 'extra',
                title: '备注',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                align: 'center',
                formatter: function(value,row,index){
                    if(row.blacklist == "正常")
                        return '<a onclick="blackList(\''+row.wechat_id+'\')">拉黑</a> | <a onclick="beMaster(\''+row.wechat_id+'\')">升级</a>';
                }
            }]
        ]
    });
    $('#manageApprentice_dg').datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getApprenticeList(pageNumber-1);
        }
    });
});

function onClickCell(index, field){
    if (endEditing()){
        $('#manageApprentice_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}
//获取徒弟列表
function getApprenticeList(pageNum)
{
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = 24;
    data["page"] = pageNum;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                var row = [];
                var count = res.count[0];
                for(var i=0;i<res.data.length;i++)
                {
                    if(res.data[i].role == "徒弟")
                    {
                        row.push(res.data[i]);
                    }
                    $("#manageApprentice_dg").datagrid('loadData',{ total: count['0'], rows: row });
                }
            }
        }
    })
}
//拉黑
function blackList(username)
{
    var data = {};
    data["code"] = 22;
    data["wechat_id"] = username;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("拉黑成功");
                getApprenticeList();
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}
//升级
function beMaster(username)
{
    var data = {};
    data["code"] = 26;
    data["wechat_id"] = username;
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            if(res.code == "0")
            {
                alert("升级成功");
                getApprenticeList();
            }
            else
            {
                alert("请求失败，请重试");
            }
        }
    })
}