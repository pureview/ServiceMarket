/**
 * Created by funing on 2018/6/1.
 */
$(function(){
    $("#manageNew_dg").datagrid({
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
                field: 'introductionID',
                title: '介绍人ID',
                width: '20%',
                align: 'center'
            },
            {
                field: 'sex',
                title: '性别',
                width: '20%',
                align: 'center'
            },
            {
                field: 'age',
                title: '年龄',
                width: '20%',
                align: 'center'
            },
            {
                field: 'transaction',
                title: '交易图片',
                width: '20%',
                align: 'center'
            },
            {
                field: 'operate',
                title: '操作',
                width: '22%',
                align: 'center',
                formatter: function(value,row,index){
                    return '<a href="#">通过</a> | <a href="#">拒绝</a>';
                }
            }]
        ]
    })
});

function onClickCell(index, field){
    if (endEditing()){
        $('#manageNew_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}