from django.shortcuts import render

# home (首頁)
def home(request):
    # index.html 
    return render(request, 'index.html')

# ⬇️⬇️⬇️ 新增：專門給圖表呼叫的數據 API ⬇️⬇️⬇️
def dashboard_api(request):
    # 1. 計算「各單位」有幾名員工
    dept_data = Employee.objects.values('department').annotate(count=Count('id'))
    # 把空的單位標記為「未分類」
    dept_labels = [item['department'] if item['department'] else '未分類' for item in dept_data]
    dept_counts = [item['count'] for item in dept_data]

    # 2. 計算「各系統」被配置了多少個帳號
    sys_data = Account.objects.values('system__name').annotate(count=Count('id'))
    sys_labels = [item['system__name'] for item in sys_data]
    sys_counts = [item['count'] for item in sys_data]

    # 把算好的資料打包成 JSON 傳給前端
    return JsonResponse({
        'dept_labels': dept_labels,
        'dept_counts': dept_counts,
        'sys_labels': sys_labels,
        'sys_counts': sys_counts,
    })