# -*- coding: utf-8 -*-
"""
Web服务器并发性能可视化测试脚本
"""
import threading
import requests
import time
import matplotlib.pyplot as plt
import matplotlib

# 设置图表支持显示中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 测试配置
TARGET_URL = 'http://127.0.0.1:8080/index.html'
NUM_CLIENTS = 10  # 模拟同时发起请求的客户端数量

results = []
lock = threading.Lock()
# 使用 Event 充当发令枪，确保所有线程真正做到“同时起跑”
start_gun = threading.Event()

def send_request(client_id):
    # 所有线程运行到这里都会阻塞，等待发令枪响
    start_gun.wait() 
    
    req_start = time.time()
    try:
        # 向服务器发起请求
        response = requests.get(TARGET_URL, timeout=10)
        status = response.status_code
    except Exception as e:
        status = f"Error: {type(e).__name__}"
    req_end = time.time()
    
    # 将测试结果安全地存入列表
    with lock:
        results.append({
            'id': client_id,
            'start': req_start,
            'end': req_end,
            'duration': req_end - req_start,
            'status': status
        })

def run_test():
    print(f"正在准备 {NUM_CLIENTS} 个并发线程...")
    threads = []
    for i in range(NUM_CLIENTS):
        t = threading.Thread(target=send_request, args=(i+1,))
        threads.append(t)
        t.start()
    
    # 给系统一点时间完成线程的创建和就绪
    time.sleep(0.5) 
    print("发令枪响！所有线程同时发起请求...")
    
    # 记录全局起始时间，并开枪放行所有线程
    global_start_time = time.time()
    start_gun.set() 
    
    # 等待所有线程执行完毕
    for t in threads:
        t.join()
        
    print("测试完成，正在生成可视化图表...")
    plot_results(global_start_time)

def plot_results(global_start_time):
    # 根据客户端 ID 排序，保证图表美观
    results.sort(key=lambda x: x['id'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 绘制每个请求的时间条（甘特图）
    for res in results:
        client_id = res['id']
        start_offset = res['start'] - global_start_time
        duration = res['duration']
        
        # 状态码 200 为绿色，其他报错为红色
        color = '#4CAF50' if res['status'] == 200 else '#F44336'
        
        # 画水平条
        ax.barh(client_id, duration, left=start_offset, color=color, 
                edgecolor='black', alpha=0.8, height=0.5)
        
        # 在条形图右侧标注耗时和状态
        ax.text(start_offset + duration + 0.02, client_id, 
                f"{duration:.3f}s (HTTP {res['status']})", 
                va='center', fontsize=9)

    ax.set_xlabel('时间进度 (秒)')
    ax.set_ylabel('模拟客户端 ID')
    ax.set_title('Simple Web Server 多线程并发性能测试图')
    ax.set_yticks(range(1, NUM_CLIENTS + 1))
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    run_test()