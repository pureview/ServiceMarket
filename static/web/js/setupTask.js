/**
 * Created by funing on 2018/6/17.
 */
//获取店铺列表
function getShopList()
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
            var data = [];
            if(res.code == "0")
            {
                for(var i=0; i<res.data.length; i++)
                {
                    var shop = {};
                    shop["id"] = res.data[i].shop;
                    shop["text"] = res.data[i].shop;
                    data.push(shop);
                }
            }
            $("#shopList").combobox("loadData", data);
        }
    })
}

//创建任务
function setupTask()
{
    var key = $("input[name=keyword]");
    var keyword = [];
    for(var i=0;i<key.length;i++)
    {
        keyword.push($(key[i]).val());
    }
    var count = $("input[name=count]");
    var c = [];
    for(var i=0;i<count.length;i++)
    {
        c.push($(count[i]).val());
    }

    var shop = $("#shopList").val();
    var good_name = $("#good_name").val();
    var sort = $("input:radio[name=sort]:checked").val();
    var price_lower = $("#price1").val();
    var price_higher = $("#price2").val();
    var good_price = $("#good_price").val();
    var good_num = $("#num").val();
    var keywords = keyword.join(" ");
    var mission_nums = c.join(" ");
    var begin_time = changeTime($("#begin_time").val());
    var end_time = changeTime($("#end_time").val());
    var allow = $("input:radio[name=allow]:checked").val();
    var master_money = $("#master_money").val();
    var slave_money = ($("#salve_money").val()=="")?"0":$("#salve_money").val();
    var img = document.getElementById("images").files[0];

    if(shop != "" && good_name != "" && sort != "" && good_price != "" && good_num != "" && keywords != "" && mission_nums != "" && begin_time != "" && end_time != "" && allow != "" && master_money != "" && slave_money != "" && img != null)
    {
        var data = new FormData();
        data.append("code","0");
        data.append("seller_username",window.localStorage.getItem("username"));
        data.append("shop",shop);
        data.append("images",img);
        data.append("good_name",good_name);
        data.append("sort",sort);
        if(price_lower != "" && price_higher != "")
        {
            data.append("price_lower",price_lower);
            data.append("price_higher",price_higher);
        }
        data.append("good_price",good_price);
        data.append("good_num",good_num);
        data.append("keywords",keywords);
        data.append("mission_nums", mission_nums);
        data.append("begin_time", begin_time);
        data.append("end_time", end_time);
        data.append("allow", allow);
        data.append("master_money",master_money);
        data.append("slave_money",slave_money);
        console.log(data);
        $.ajax({
            url: url,
            type: 'post',
            data: data,
            dataType: 'JSON',
            processData : false,
            contentType : false,
            success: function(res){
                if(res.code == "0")
                {
                    alert("发布成功");
                    window.location.reload();
                }
            }
        })
    }else
    {
        alert("请填写完整信息");
    }
}

//重新发布任务
function reSet(id)
{
    var data = {};
    data["code"] = 6;
    data["seller_username"] = window.localStorage.getItem("username");
    data["mission_id"] = id;
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            if(res.code == "0")
            {
                var data=res.data;
                console.log(data);
                var shop = data.shop;
                var good_name = data.good_name;
                var sort = data.sort;
                var price_lower = data.price_lower;
                var price_higher = data.price_higher;
                var good_price = data.good_price;
                var good_num = data.good_num;
                var keyword = data.keyword;
                var mission_num = data.mission_num.toString();
                var allow = data.allow;
                var master_money = data.master_money;
                var slave_money = data.slave_money;

                $("#shopList").combobox("setValue",shop);
                $("#good_name").textbox("setValue",good_name);
                $("input:radio[name=sort][value="+sort+"]").prop("checked","checked");
                $("#price1").textbox("setValue",price_lower);
                $("#price2").textbox("setValue",price_higher);
                $("#good_price").numberbox("setValue",good_price);
                $("#num").textbox("setValue",good_num);
                var key = keyword.split(",");
                var num = mission_num.split(",");
                $("#allKey").html("");
                for(var i=0;i<key.length;i++)
                {
                    var html = $('<div name="'+i+'">搜索关键词： <input name="keyword" class="easyui-textbox textbox" style="width:30%;height:32px;margin:5px" value="'+key[i]+'">添加<input name="count" class="easyui-numberbox textbox" style="width:10%;height:32px;margin:5px" value="'+num[i]+'">单 <a onclick="deleteKeyword(\''+i+'\')">删除</a> </div>');
                    $("#allKey").append(html);
                }
                $("input:radio[name=allow][value="+allow+"]").prop("checked","checked");
                $("#master_money").numberbox("setValue",master_money);
                if(slave_money != 0)
                {
                    $("#salve_money").numberbox("setValue",slave_money);
                    $("#salve").css("display","inline-block");
                }
            }
        }
    });
    window.localStorage.removeItem("mission_id");
}