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
    var price_lower = $("#price1").val();
    var price_higher = $("#price2").val();
    var good_place = $("#place").val();
    var extra = $("#other").val();


    if(shop != "" && good_name != "" && sort != "" && good_price != "" && good_num != "" && keywords != "" && mission_nums != "" && begin_time != "" && end_time != "" && allow != "" && master_money != "" && slave_money != "" && img != null)
    {
        var data = new FormData();
        data.append("code","0");
        data.append("seller_username",window.localStorage.getItem("username"));
        data.append("shop",shop);
        data.append("images",img);
        data.append("good_name",good_name);
        data.append("sort",sort);
        if(document.getElementById("priceCheck").checked)
        {
            data.append("price_lower",price_lower);
            data.append("price_higher",price_higher);
        }
        if(document.getElementById("payCheck").checked)
        {
            data.append("cash_on_delivery",1);
        }
        if(document.getElementById("placeCheck").checked)
        {
            data.append("good_place", good_place);
        }
        if(document.getElementById("otherCheck").checked)
        {
            data.append("extra", extra);
        }
        data.append("good_price",good_price);
        data.append("good_num",good_num);
        data.append("keywords",keywords);
        data.append("mission_nums", mission_nums);
        data.append("begin_time", begin_time);
        data.append("end_time", end_time);
        data.append("allow", allow);
        data.append("slave_money",master_money);
        data.append("master_money",slave_money);
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
                else{
                    alert("发布失败");
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
                var good_place = data.good_place;
                var extra = data.extra;
                var cash_on_delivery = data.cash_on_delivery;
                var good_price = data.good_price;
                var good_num = data.good_num;
                var keyword = data.keywords;
                var mission_num = data.mission_nums.toString();
                var allow = data.allow;
                var master_money = data.master_money;//提成
                var slave_money = data.slave_money;//基本
                window.localStorage.setItem("good_name",good_name);

                $("#shopList").combobox("setValue",shop);
                $("#good_name").textbox("setValue",good_name);
                console.log($("#good_name").val());
                $("input:radio[name=sort][value="+sort+"]").prop("checked","checked");
                $("#price1").textbox("setValue",price_lower);
                $("#price2").textbox("setValue",price_higher);
                $("#good_price").numberbox("setValue",good_price);
                $("#num").textbox("setValue",good_num);

                $("#shopList").combobox("setValue",shop);
                $("#good_name").textbox("setValue",good_name);
                $("input:radio[name=sort][value="+sort+"]").prop("checked","checked");
                if(price_lower != 0 && price_higher != 0)
                {
                    $("#price1").textbox("setValue",price_lower);
                    $("#price2").textbox("setValue",price_higher);
                    $("#priceCheck").attr("checked","checked");
                }
                if(cash_on_delivery == 1)
                {
                    $("#payCheck").attr("checked","checked");
                }
                if(extra != "")
                {
                    $("#other").textbox("setValue",extra);
                    $("#otherCheck").attr("checked","checked");
                }
                if(good_place != "")
                {
                    $("#place").textbox("setValue",good_place);
                    $("#placeCheck").attr("checked","checked");
                }

                $("#good_price").numberbox("setValue",good_price);
                $("#num").textbox("setValue",good_num);
                var key = keyword.split(" ");
                var num = mission_num.split(" ");
                $("#allKey").html("");
                for(var i=0;i<key.length;i++)
                {
                    var html = $('<div name="'+i+'">搜索关键词： <input name="keyword" class="easyui-textbox textbox" style="width:30%;height:32px;margin:5px" value="'+key[i]+'">添加<input name="count" class="easyui-numberbox textbox" style="width:10%;height:32px;margin:5px" value="'+num[i]+'">单 <a onclick="deleteKeyword(\''+i+'\')">删除</a> </div>');
                    $("#allKey").append(html);
                }
                $("input:radio[name=allow][value="+allow+"]").prop("checked","checked");
                $("#master_money").numberbox("setValue",slave_money);
                if(master_money != 0)
                {
                    $("#salve_money").numberbox("setValue",master_money);
                    $("#salve").css("display","inline-block");
                }
            }
        }
    });
    window.localStorage.removeItem("mission_id");
}


//获取订单列表
function getOrderList(pageNum)
{
    var mission_id = window.localStorage.getItem("task_id");
    var begin_time = $("#begin_date").val();
    var end_time = $("#end_date").val();
    var status = $("#status").val();
    var shop =$("#shop").val();
    var good_name = $("#good_name").val();
    if(pageNum == null)
        pageNum = 0;
    var data = {};
    data["code"] = "10";
    data["seller_username"] = window.localStorage.getItem("username");
    data["page"] = pageNum;
    if(mission_id != "null")
    {
        data["mission_id"] = mission_id;
    }
    else{
        if(status != "全部")
        {
            data["status"] = status;
        }
        if(shop != "全部")
        {
            data["shop"] = shop;
        }
        if(begin_time != "" && end_time != "")
        {
            data["begin_time"] = getTodayTime(begin_time);
            data["end_time"] = getTodayTime(end_time);
        }
        if(good_name != "")
        {
            data["good_name"] = good_name;
        }
    }
    console.log(data);
    $.ajax({
        url: url,
        type: 'post',
        data: data,
        success: function(res){
            res = JSON.parse(res);
            console.log(res);
            var count = res.count[0];
            if(res.code == "0")
            {
                var row = [];
                for(var i=0;i<res.data.length;i++)
                {
                    row.push(res.data[i]);
                }
                $("#manageOrder_dg").datagrid('loadData',{ total: count['0'], rows: row });
                //window.localStorage.setItem("task_id",null);
            }
        }
    })
}