/**
 * SSH凭证管理页面的JavaScript
 */

$(function() {
    // 初始化Select2
    $('.select2').select2({
        theme: 'bootstrap4',
        placeholder: '请选择主机',
        allowClear: true
    });
    
    // 加载主机列表到Select2
    loadHostsForSelect();
    
    // 加载凭证列表
    loadCredentials();
    
    // 搜索按钮点击事件
    $('#searchBtn').on('click', function() {
        loadCredentials(1);
    });
    
    // 搜索框回车事件
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) {
            loadCredentials(1);
            return false;
        }
    });
    
    // 全选/取消全选
    $('#selectAll').on('change', function() {
        $('.credential-checkbox').prop('checked', $(this).prop('checked'));
    });
    
    // 认证类型切换事件
    $('input[name="auth_type"]').on('change', function() {
        const authType = $(this).val();
        if (authType === 'password') {
            $('#passwordAuthSection').show();
            $('#keyAuthSection').hide();
        } else {
            $('#passwordAuthSection').hide();
            $('#keyAuthSection').show();
        }
    });
    
    // 密码显示/隐藏切换
    $('.toggle-password').on('click', function() {
        const passwordField = $(this).closest('.input-group').find('input');
        const type = passwordField.attr('type') === 'password' ? 'text' : 'password';
        passwordField.attr('type', type);
        $(this).find('i').toggleClass('fa-eye fa-eye-slash');
    });
    
    // 保存凭证按钮点击事件
    $('#saveCredentialBtn').on('click', function() {
        saveCredential();
    });
    
    // 测试连接按钮点击事件
    $('#testCredentialBtn').on('click', function() {
        testConnection();
    });
});

/**
 * 加载凭证列表
 * @param {number} page 页码
 */
function loadCredentials(page = 1) {
    const search = $('#searchInput').val();
    
    $.ajax({
        url: '/hosts/api/credentials/list/',
        type: 'GET',
        data: {
            page: page,
            search: search
        },
        success: function(response) {
            renderCredentialTable(response);
            renderPagination(response);
        },
        error: function(xhr) {
            showToast('error', '加载凭证列表失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 渲染凭证表格
 * @param {Object} data 凭证数据
 */
function renderCredentialTable(data) {
    const tableBody = $('#credentialTableBody');
    tableBody.empty();
    
    if (data.credentials.length === 0) {
        tableBody.append(`
            <tr>
                <td colspan="8" class="text-center">没有找到凭证记录</td>
            </tr>
        `);
        return;
    }
    
    data.credentials.forEach(function(credential) {
        tableBody.append(`
            <tr>
                <td>
                    <input type="checkbox" class="credential-checkbox" value="${credential.id}">
                </td>
                <td>${credential.name}</td>
                <td>${credential.username}</td>
                <td>
                    <span class="badge ${credential.auth_type === '密码' ? 'badge-primary' : 'badge-success'}">
                        ${credential.auth_type}
                    </span>
                </td>
                <td>${credential.host_count}</td>
                <td>${credential.created_by}</td>
                <td>${credential.created_at}</td>
                <td>
                    <button type="button" class="btn btn-info btn-sm" onclick="viewCredential(${credential.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button type="button" class="btn btn-primary btn-sm" onclick="editCredential(${credential.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm" onclick="deleteCredential(${credential.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `);
    });
}

/**
 * 渲染分页控件
 * @param {Object} data 分页数据
 */
function renderPagination(data) {
    const pagination = $('#pagination');
    pagination.empty();
    
    // 更新分页信息
    $('#paginationInfo').text(`显示第 ${(data.page - 1) * 10 + 1} 至 ${Math.min(data.page * 10, data.total)} 项，共 ${data.total} 项`);
    
    // 如果只有一页，不显示分页控件
    if (data.total_pages <= 1) {
        return;
    }
    
    // 构建分页HTML
    let paginationHtml = `
        <ul class="pagination">
            <li class="paginate_button page-item previous ${data.page === 1 ? 'disabled' : ''}">
                <a href="javascript:void(0)" class="page-link" onclick="loadCredentials(${data.page - 1})">上一页</a>
            </li>
    `;
    
    // 显示页码
    const startPage = Math.max(1, data.page - 2);
    const endPage = Math.min(data.total_pages, data.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHtml += `
            <li class="paginate_button page-item ${i === data.page ? 'active' : ''}">
                <a href="javascript:void(0)" class="page-link" onclick="loadCredentials(${i})">${i}</a>
            </li>
        `;
    }
    
    paginationHtml += `
            <li class="paginate_button page-item next ${data.page === data.total_pages ? 'disabled' : ''}">
                <a href="javascript:void(0)" class="page-link" onclick="loadCredentials(${data.page + 1})">下一页</a>
            </li>
        </ul>
    `;
    
    pagination.html(paginationHtml);
}

/**
 * 加载主机列表到Select2
 */
function loadHostsForSelect() {
    $.ajax({
        url: '/hosts/api/hosts/',
        type: 'GET',
        success: function(response) {
            const hostsSelect = $('#hosts');
            hostsSelect.empty();
            
            response.forEach(function(host) {
                hostsSelect.append(new Option(`${host.hostname} (${host.ip_address})`, host.id));
            });
        },
        error: function(xhr) {
            showToast('error', '加载主机列表失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 保存凭证
 */
function saveCredential() {
    const form = $('#addCredentialForm');
    
    // 表单验证
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // 获取表单数据
    const formData = new FormData(form[0]);
    const authType = $('input[name="auth_type"]:checked').val();
    
    // 根据认证类型验证必填字段
    if (authType === 'password' && !formData.get('password')) {
        showToast('error', '验证失败', '密码认证类型必须提供密码');
        return;
    }
    
    if (authType === 'key' && !formData.get('private_key')) {
        showToast('error', '验证失败', '密钥认证类型必须提供私钥');
        return;
    }
    
    // 转换为JSON数据
    const jsonData = {};
    formData.forEach((value, key) => {
        if (key === 'hosts') {
            // 处理多选的主机
            const hostIds = $('#hosts').val();
            jsonData.host_ids = hostIds;
        } else {
            jsonData[key] = value;
        }
    });
    
    // 发送请求
    $.ajax({
        url: '/hosts/api/credentials/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(jsonData),
        success: function(response) {
            showToast('success', '保存成功', '凭证已成功保存');
            $('#addCredentialModal').modal('hide');
            loadCredentials();
            form[0].reset();
        },
        error: function(xhr) {
            showToast('error', '保存失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 测试连接
 */
function testConnection() {
    const form = $('#addCredentialForm');
    const hostId = $('#hosts').val()[0]; // 获取第一个选中的主机ID
    
    if (!hostId) {
        showToast('warning', '测试连接', '请选择至少一个主机进行测试');
        return;
    }
    
    // 表单验证
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // 获取表单数据
    const formData = new FormData(form[0]);
    const authType = $('input[name="auth_type"]:checked').val();
    
    // 根据认证类型验证必填字段
    if (authType === 'password' && !formData.get('password')) {
        showToast('error', '验证失败', '密码认证类型必须提供密码');
        return;
    }
    
    if (authType === 'key' && !formData.get('private_key')) {
        showToast('error', '验证失败', '密钥认证类型必须提供私钥');
        return;
    }
    
    // 显示测试中提示
    showToast('info', '测试连接', '正在测试连接，请稍候...');
    
    // 转换为JSON数据
    const jsonData = {};
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });
    
    // 添加主机ID
    jsonData.host_id = hostId;
    
    // 发送请求
    $.ajax({
        url: '/hosts/test-ssh/',
        type: 'POST',
        data: jsonData,
        success: function(response) {
            if (response.success) {
                showToast('success', '测试成功', response.message);
            } else {
                showToast('error', '测试失败', response.message);
            }
        },
        error: function(xhr) {
            showToast('error', '测试失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 查看凭证详情
 * @param {number} id 凭证ID
 */
function viewCredential(id) {
    $.ajax({
        url: `/hosts/api/credentials/${id}/`,
        type: 'GET',
        success: function(response) {
            renderCredentialDetail(response);
            $('#credentialDetailModal').modal('show');
        },
        error: function(xhr) {
            showToast('error', '获取凭证详情失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 渲染凭证详情
 * @param {Object} credential 凭证数据
 */
function renderCredentialDetail(credential) {
    const detailContent = $('#credentialDetailContent');
    detailContent.empty();
    
    // 构建详情HTML
    const detailHtml = `
        <div class="row">
            <div class="col-md-6">
                <div class="form-group">
                    <label>凭证名称:</label>
                    <p>${credential.name}</p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-group">
                    <label>用户名:</label>
                    <p>${credential.username}</p>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="form-group">
                    <label>认证类型:</label>
                    <p>
                        <span class="badge ${credential.auth_type === '密码' ? 'badge-primary' : 'badge-success'}">
                            ${credential.auth_type}
                        </span>
                    </p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-group">
                    <label>是否默认:</label>
                    <p>
                        <span class="badge ${credential.is_default ? 'badge-success' : 'badge-secondary'}">
                            ${credential.is_default ? '是' : '否'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <div class="form-group">
                    <label>创建人:</label>
                    <p>${credential.created_by}</p>
                </div>
            </div>
            <div class="col-md-6">
                <div class="form-group">
                    <label>创建时间:</label>
                    <p>${credential.created_at}</p>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col-12">
                <div class="form-group">
                    <label>描述:</label>
                    <p>${credential.description || '无'}</p>
                </div>
            </div>
        </div>
    `;
    
    detailContent.html(detailHtml);
    
    // 渲染关联主机列表
    const hostsTableBody = $('#credentialHostsTableBody');
    hostsTableBody.empty();
    
    if (credential.hosts.length === 0) {
        hostsTableBody.append(`
            <tr>
                <td colspan="4" class="text-center">没有关联的主机</td>
            </tr>
        `);
        return;
    }
    
    credential.hosts.forEach(function(host) {
        hostsTableBody.append(`
            <tr>
                <td>${host.hostname}</td>
                <td>${host.ip_address}</td>
                <td>
                    <span class="badge ${getStatusBadgeClass(host.status)}">
                        ${host.status}
                    </span>
                </td>
                <td>${host.os_type || 'Unknown'}</td>
            </tr>
        `);
    });
}

/**
 * 获取状态对应的Badge类名
 * @param {string} status 状态
 * @returns {string} Badge类名
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case '在线':
            return 'badge-success';
        case '离线':
            return 'badge-danger';
        case '维护中':
            return 'badge-warning';
        default:
            return 'badge-secondary';
    }
}

/**
 * 编辑凭证
 * @param {number} id 凭证ID
 */
function editCredential(id) {
    // 重置表单
    $('#addCredentialForm')[0].reset();
    
    // 修改模态框标题
    $('#addCredentialModalLabel').text('编辑SSH凭证');
    
    // 加载凭证数据
    $.ajax({
        url: `/hosts/api/credentials/${id}/`,
        type: 'GET',
        success: function(credential) {
            // 填充表单数据
            $('#name').val(credential.name);
            $('#username').val(credential.username);
            $(`input[name="auth_type"][value="${credential.auth_type.toLowerCase()}"]`).prop('checked', true).trigger('change');
            
            // 设置关联主机
            const hostIds = credential.hosts.map(host => host.id);
            $('#hosts').val(hostIds).trigger('change');
            
            // 设置描述
            $('#description').val(credential.description);
            
            // 显示模态框
            $('#addCredentialModal').modal('show');
            
            // 修改保存按钮点击事件
            $('#saveCredentialBtn').off('click').on('click', function() {
                updateCredential(id);
            });
        },
        error: function(xhr) {
            showToast('error', '获取凭证数据失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 更新凭证
 * @param {number} id 凭证ID
 */
function updateCredential(id) {
    const form = $('#addCredentialForm');
    
    // 表单验证
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // 获取表单数据
    const formData = new FormData(form[0]);
    const authType = $('input[name="auth_type"]:checked').val();
    
    // 根据认证类型验证必填字段
    if (authType === 'password' && !formData.get('password')) {
        // 编辑时密码可以为空，表示不修改密码
    } else if (authType === 'key' && !formData.get('private_key')) {
        // 编辑时私钥可以为空，表示不修改私钥
    }
    
    // 转换为JSON数据
    const jsonData = {};
    formData.forEach((value, key) => {
        if (key === 'hosts') {
            // 处理多选的主机
            const hostIds = $('#hosts').val();
            jsonData.host_ids = hostIds;
        } else if ((key === 'password' || key === 'private_key' || key === 'passphrase') && !value) {
            // 跳过空的敏感字段，表示不修改
        } else {
            jsonData[key] = value;
        }
    });
    
    // 发送请求
    $.ajax({
        url: `/hosts/api/credentials/${id}/`,
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(jsonData),
        success: function(response) {
            showToast('success', '更新成功', '凭证已成功更新');
            $('#addCredentialModal').modal('hide');
            loadCredentials();
            
            // 重置表单和按钮事件
            form[0].reset();
            $('#addCredentialModalLabel').text('添加SSH凭证');
            $('#saveCredentialBtn').off('click').on('click', function() {
                saveCredential();
            });
        },
        error: function(xhr) {
            showToast('error', '更新失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}

/**
 * 删除凭证
 * @param {number} id 凭证ID
 */
function deleteCredential(id) {
    if (!confirm('确定要删除此凭证吗？此操作不可恢复。')) {
        return;
    }
    
    $.ajax({
        url: `/hosts/api/credentials/${id}/delete/`,
        type: 'POST',
        success: function(response) {
            showToast('success', '删除成功', response.message);
            loadCredentials();
        },
        error: function(xhr) {
            showToast('error', '删除失败', xhr.responseJSON?.error || '服务器错误');
        }
    });
}