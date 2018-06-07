/**
 * Created by funing on 2018/5/31.
 */
$(function(){
    $("#fundDetail_dg").datagrid({
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
                field: 'totalFund',
                title: '总佣金花费',
                width: '20%',
                align: 'center'
            },
            {
                field: 'totalCapital',
                title: '总本金花费',
                width: '20%',
                align: 'center'
            },
            {
                field: 'totalNum',
                title: '总单数',
                width: '20%',
                align: 'center'
            },
            {
                field: 'master',
                title: '师父佣金',
                width: '20%',
                align: 'center'
            },
            {
                field: 'apprentice',
                title: '徒弟佣金',
                width: '20%',
                align: 'center'
            }]
        ]
    })
});

function onClickCell(index, field){
    if (endEditing()){
        $('#fundDetail_dg').datagrid('selectRow', index)
            .datagrid('editCell', {index:index,field:field});
        editIndex = index;
    }
}