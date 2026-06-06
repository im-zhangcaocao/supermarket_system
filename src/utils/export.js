import * as XLSX from 'xlsx';

export function exportToExcel(data, filename, columns) {
  if (!data || data.length === 0) {
    return false;
  }

  const ws = XLSX.utils.json_to_sheet(data, { 
    header: columns.map(col => col.prop),
    skipHeader: true,
    origin: 'A2'
  });

  const columnWidths = columns.map((col, i) => {
    const maxLen = Math.max(
      col.label.length,
      ...data.map(row => {
        const val = row[col.prop];
        return val ? String(val).length : 0;
      })
    );
    return { wch: Math.min(maxLen + 2, 50) };
  });

  ws['!cols'] = columnWidths;

  const headerRow = columns.map(col => col.label);
  XLSX.utils.sheet_add_aoa(ws, [headerRow], { origin: 'A1' });

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');

  XLSX.writeFile(wb, `${filename}.xlsx`);
  return true;
}

export function exportFinancialRecords(records, filename) {
  const columns = [
    { prop: 'record_id', label: '记录ID' },
    { prop: 'type', label: '类型' },
    { prop: 'amount', label: '金额' },
    { prop: 'relate_order_id', label: '关联订单' },
    { prop: 'occur_time', label: '发生时间' },
    { prop: 'remark', label: '备注' }
  ];

  const data = records.map(r => ({
    ...r,
    type: r.type === 1 ? '收入' : '支出'
  }));

  return exportToExcel(data, filename, columns);
}

export function exportSalesReport(dates, amounts, counts, filename) {
  const data = dates.map((date, i) => ({
    '日期': date,
    '销售额': amounts[i],
    '订单数': counts[i]
  }));

  const columns = [
    { prop: '日期', label: '日期' },
    { prop: '销售额', label: '销售额' },
    { prop: '订单数', label: '订单数' }
  ];

  return exportToExcel(data, filename, columns);
}

export function exportTableData(data, columns, filename) {
  return exportToExcel(data, filename, columns);
}