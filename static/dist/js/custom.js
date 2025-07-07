/**
 * 运维平台自定义JavaScript
 * 包含全局函数和工具方法
 */

// 通知消息显示
function showNotification(type, message, title = '') {
    // 使用toastr插件显示通知
    toastr.options = {
        closeButton: true,
        progressBar: true,
        positionClass: "toast-top-right",
        timeOut: "3000"
    };
    
    switch(type) {
        case 'success':
            toastr.success(message, title);
            break;
        case 'info':
            toastr.info(message, title);
            break;
        case 'warning':
            toastr.warning(message, title);
            break;
        case 'error':
            toastr.error(message, title);
            break;
        default:
            toastr.info(message, title);
    }
}

// AJAX请求封装
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    // 获取CSRF Token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    $.ajax({
        url: url,
        type: method,
        data: data,
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            if (successCallback && typeof successCallback === 'function') {
                successCallback(response);
            }
        },
        error: function(xhr, status, error) {
            console.error('AJAX Error:', error);
            if (errorCallback && typeof errorCallback === 'function') {
                errorCallback(xhr, status, error);
            } else {
                showNotification('error', '请求失败: ' + error);
            }
        }
    });
}

// 确认对话框
function confirmAction(title, message, confirmCallback, cancelCallback) {
    Swal.fire({
        title: title,
        text: message,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '确认',
        cancelButtonText: '取消'
    }).then((result) => {
        if (result.isConfirmed && confirmCallback) {
            confirmCallback();
        } else if (cancelCallback) {
            cancelCallback();
        }
    });
}

// 格式化日期时间
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 格式化执行时长（秒）
function formatDuration(seconds) {
    if (seconds === null || seconds === undefined) return '-';
    
    if (seconds < 60) {
        return seconds.toFixed(2) + ' 秒';
    } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = (seconds % 60).toFixed(0);
        return minutes + ' 分 ' + remainingSeconds + ' 秒';
    } else {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = ((seconds % 3600) % 60).toFixed(0);
        return hours + ' 小时 ' + minutes + ' 分 ' + remainingSeconds + ' 秒';
    }
}

// 初始化Select2
function initSelect2(selector, options = {}) {
    const defaultOptions = {
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择...',
        allowClear: true
    };
    
    $(selector).select2({
        ...defaultOptions,
        ...options
    });
}

// 初始化DataTables
function initDataTable(selector, options = {}) {
    const defaultOptions = {
        language: {
            url: '/static/plugins/datatables/Chinese.json'
        },
        responsive: true,
        autoWidth: false
    };
    
    return $(selector).DataTable({
        ...defaultOptions,
        ...options
    });
}

// 文档加载完成后执行
$(document).ready(function() {
    // 初始化工具提示
    $('[data-toggle="tooltip"]').tooltip();
    
    // 初始化弹出框
    $('[data-toggle="popover"]').popover();
    
    // 侧边栏激活状态
    const currentPath = window.location.pathname;
    $('.nav-sidebar .nav-link').each(function() {
        const linkPath = $(this).attr('href');
        if (currentPath === linkPath) {
            $(this).addClass('active');
            $(this).closest('.nav-item').addClass('menu-open');
            $(this).closest('.nav-treeview').prev().addClass('active');
        }
    });
});