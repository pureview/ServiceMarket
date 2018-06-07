/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    $("#manageTask_dg").datagrid({
        url:'datagrid_data1.json',
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
                field: 'choose',
                width: '10%',
                align: 'center',
                checkbox: true
            },
            {
                field: 'status',
                title: '任务状态',
                width: '10%',
                align: 'center'
            },
            {
                field: 'taskNum',
                title: '任务数量',
                width: '10%',
                align: 'center',
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写任务数量'
                    }
                }
            },
            {
                field: 'count',
                title: '商品数量',
                width: '10%',
                align: 'center',
                editor: {
                    type: 'validatebox',
                    options:{
                        required: true,
                        missingMessage:'请填写商品数量'
                    }
                }
            },
            {
                field: 'startTime',
                title: '开始时间',
                width: '15%',
                align: 'center',
                formatter: myformatter,
                editor: {
                    type: 'datetimebox',
                    options: {
                        required: true,
                        missingMessage:'请选择开始时间'
                    }
                }
            },
            {
                field: 'endTime',
                title: '结束时间',
                width: '15%',
                align: 'center',
                formatter: myformatter,
                editor: {
                    type: 'datetimebox',
                    options: {
                        required: true,
                        missingMessage: '请选择结束时间'
                    }
                }
            },
            {
                field: 'master',
                title: '师父佣金',
                width: '10%',
                align: 'center',
                editor: {
                    type: 'validatebox',
                    options: {
                        required: true,
                        missingMessage: '请输入师父佣金'
                    }
                }
            },
            {
                field: 'apprentice',
                title: '徒弟佣金',
                width: '10%',
                align: 'center',
                editor: {
                    type: 'validatebox',
                    options: {
                        required: true,
                        missingMessage: '请输入徒弟佣金'
                    }
                }
            },
            {
                field: 'relation',
                title: '选择',
                width: '10%',
                align: 'center',
                editor: {
                    type: 'combobox',
                    options: {
                        data: [{value:'全部',text:'全部'},{value:'师父',text:'师父'}],
                        valueFiled: 'value',
                        textFiled: 'text',
                        panelHeight: 'auto',
                        required: true,
                        missingMessage: "请选择一项"
                    }
                }
            },
            {
                field: 'operate',
                title: '操作',
                width: '10%',
                align: 'center',
                formatter: function(value,row,index){
                    return '<a href="#">取消任务</a>';
                }
            }]
        ],
        toolbar: [
            {
                text: '保存编辑',
                iconCls: 'icon-save'
            },
            {
                text: '发布任务'
            }
        ]
    });
});
//设置单元格可编辑
$.extend($.fn.datagrid.methods, {
    editCell: function(jq,param){
        return jq.each(function(){
            var opts = $(this).datagrid('options');
            var fields = $(this).datagrid('getColumnFields',true).concat($(this).datagrid('getColumnFields'));
            for(var i=0; i<fields.length; i++){
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor1 = col.editor;
                if (fields[i] != param.field){
                    col.editor = null;
                }
            }
            $(this).datagrid('beginEdit', param.index);
            for(var i=0; i<fields.length; i++){
                var col = $(this).datagrid('getColumnOption', fields[i]);
                col.editor = col.editor1;
            }
        });
    }
});

var editIndex = undefined;
function endEditing(){
    if (editIndex == undefined){return true}
    if ($('#manageTask_dg').datagrid('validateRow', editIndex)){
        $('#manageTask_dg').datagrid('endEdit', editIndex);
        editIndex = undefined;
        return true;
    } else {
        return false;
    }
}
function onClickCell(index, field){
    if (endEditing()){
        $('#manageTask_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}
//设置时间格式
function myformatter(date){
    date= new Date(Date.parse(date));
    if(date == 'Invalid Date')
        date = new Date();
    var y = date.getFullYear();
    var m = date.getMonth()+1;
    var d = date.getDate();
    var h = date.getHours();
    var n = date.getMinutes();
    return y+(m<10?('0'+m):m)+(d<10?('0'+d):d)+'-'+(h<10?('0'+h):h)+(n<10?('0'+n):n);
}