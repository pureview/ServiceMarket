/**
 * Created by funing on 2018/6/6.
 */
/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    $("#setupShop_dg").datagrid({
        fit: true,
        rownumbers : true,
        pagination : false,
        fitColumns:true,
        singleSelect:false,
        nowrap:true,
        loadMsg: '正在加载信息.......',
        pageList : [ 20 ],
        pageSize: 20,
        idField : 'id',
        columns:[
            [{
                field: 'shop',
                title: '店铺名称',
                width: '50%',
                align: 'center'
            },
            //{
            //    field: 'mission_interval',
            //    title: '任务时间间隔',
            //    width: '30%',
            //    align: 'center',
            //    editor: {
            //        type: 'validatebox',
            //        options:{
            //            required: true,
            //            missingMessage:'请填写任务间隔'
            //        }
            //    }
            //},
            {
                field: 'operate',
                title: '操作',
                width: '20%',
                align: 'center',
                formatter: function(value,row,index){
                    return '<button onclick="deleteShop(\''+row.shop+'\')">删除</button>';
                }
            }]
        ],
        toolbar: "#span"

    });
    $('#setupShop_dg').datagrid('getPager').pagination({
        displayMsg:'当前显示第 {from}-{to} 条记录 ， 共 {total} 条记录',
        onSelectPage:function(pageNumber){
            getTaskList(pageNumber);
        }
    });
});

function openWindow()
{
    $("#shopName").textbox("setValue","");
    //$("#interval").numberbox("setValue","");
    $("#addShop").window('open');
}
//添加店铺
function addShop()
{
    if($("#shopName").val() != "")
    {
        var data = {};
        data["code"] = 16;
        data["op"] = 1;
        data["seller_username"] = window.localStorage.getItem("username");
        data["shop_name"] = $("#shopName").val();
        //data["interval"] = $("#interval").val();
        $.ajax({
            url: url,
            type: 'post',
            data: data,
            success: function(res){
                res = JSON.parse(res);
                if(res.code == "0")
                {
                    $("#addShop").window('close');
                    allShopList();
                    alert("添加店铺成功");
                }
                else
                    alert("添加失败，请重新添加");
            }
        })
    }
    else
    {
        alert('请输入店铺名称');
    }
}
//查询店铺
function allShopList()
{
    var data = {};
    data["code"] = 16;
    data["op"] = 0;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            if(res.code == "0")
            {
                var row = [];
                for(var i=0; i<res.data.length;i++)
                {
                    row.push(res.data[i]);
                }
                $("#setupShop_dg").datagrid('loadData',{ total: res.data.length, rows: row });
                $("#shop_num").text(res.data.length);
            }
        }
    })
}
//删除店铺
function deleteShop(shopName)
{
    var data = {};
    data["code"] = 16;
    data["op"] = 2;
    data["shop_name"] = shopName;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            if(res.code == "0")
            {
                alert("删除成功");
                allShopList();
            }
            else{
                alert("删除失败");
            }
        }
    })

}

//保存店铺
function updateShop(shopName,interval)
{
    var data = {};
    data["code"] = 16;
    data["op"] = 3;
    data["shop_name"] = shopName;
    data["mission_interval"] = interval;
    data["seller_username"] = window.localStorage.getItem("username");
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            if(res.code == "0")
            {
                alert("保存成功");
                allShopList();
            }
            else{
                alert("修改失败");
                allShopList();
            }
        }

    })
}