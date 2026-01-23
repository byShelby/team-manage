// 用户兑换页面JavaScript

// HTML转义函数 - 防止XSS攻击
function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// 全局变量
let currentEmail = '';
let currentCode = '';
let availableTeams = [];
let selectedTeamId = null;

// Toast提示函数
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 切换步骤
function showStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step${stepNumber}`).classList.add('active');
}

// 返回步骤1
function backToStep1() {
    showStep(1);
    selectedTeamId = null;
}

// 步骤1: 验证兑换码
document.getElementById('verifyForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value.trim();
    const code = document.getElementById('code').value.trim();
    const verifyBtn = document.getElementById('verifyBtn');

    // 验证
    if (!email || !code) {
        showToast('请填写完整信息', 'error');
        return;
    }

    // 保存到全局变量
    currentEmail = email;
    currentCode = code;

    // 禁用按钮
    verifyBtn.disabled = true;
    verifyBtn.textContent = '验证中...';

    try {
        const response = await fetch('/redeem/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            if (data.valid) {
                // 兑换码有效
                availableTeams = data.teams;

                if (availableTeams.length === 0) {
                    showToast('暂无可用的 Team', 'error');
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = '验证兑换码';
                    return;
                }

                // 显示Team列表
                renderTeamsList();
                showStep(2);
            } else {
                // 兑换码无效
                showToast(data.reason || '兑换码无效', 'error');
            }
        } else {
            showToast(data.error || '验证失败', 'error');
        }
    } catch (error) {
        showToast('网络错误,请稍后重试', 'error');
    } finally {
        verifyBtn.disabled = false;
        verifyBtn.textContent = '验证兑换码';
    }
});

// 渲染Team列表
function renderTeamsList() {
    const teamsList = document.getElementById('teamsList');
    teamsList.innerHTML = '';

    availableTeams.forEach(team => {
        const teamCard = document.createElement('div');
        teamCard.className = 'team-card';
        teamCard.onclick = () => selectTeam(team.id);

        const planBadge = team.subscription_plan === 'Plus' ? 'badge-plus' : 'badge-pro';

        teamCard.innerHTML = `
            <div class="team-name">${escapeHtml(team.team_name) || 'Team ' + team.id}</div>
            <div class="team-info">
                <div class="team-info-item">
                    <span>👥</span>
                    <span>${team.current_members}/${team.max_members} 成员</span>
                </div>
                <div class="team-info-item">
                    <span class="team-badge ${planBadge}">${escapeHtml(team.subscription_plan) || 'Plus'}</span>
                </div>
                ${team.expires_at ? `
                <div class="team-info-item">
                    <span>⏰</span>
                    <span>到期: ${formatDate(team.expires_at)}</span>
                </div>
                ` : ''}
            </div>
        `;

        teamsList.appendChild(teamCard);
    });
}

// 选择Team
function selectTeam(teamId) {
    selectedTeamId = teamId;

    // 更新UI
    document.querySelectorAll('.team-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // 立即确认兑换
    confirmRedeem(teamId);
}

// 自动选择Team
function autoSelectTeam() {
    if (availableTeams.length === 0) {
        showToast('没有可用的 Team', 'error');
        return;
    }

    // 自动选择第一个Team(后端会按过期时间排序)
    confirmRedeem(null);
}

// 确认兑换
async function confirmRedeem(teamId) {
    try {
        const response = await fetch('/redeem/confirm', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: currentEmail,
                code: currentCode,
                team_id: teamId
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 兑换成功
            showSuccessResult(data);
        } else {
            // 兑换失败
            showErrorResult(data.error || '兑换失败');
        }
    } catch (error) {
        showErrorResult('网络错误,请稍后重试');
    }
}

// 显示成功结果
function showSuccessResult(data) {
    const resultContent = document.getElementById('resultContent');
    const teamInfo = data.team_info || {};

    resultContent.innerHTML = `
        <div class="result-success">
            <div class="result-icon">✅</div>
            <div class="result-title">兑换成功!</div>
            <div class="result-message">${escapeHtml(data.message) || '您已成功加入 Team'}</div>

            <div class="result-details">
                <div class="result-detail-item">
                    <span class="result-detail-label">Team 名称</span>
                    <span class="result-detail-value">${escapeHtml(teamInfo.team_name) || '-'}</span>
                </div>
                <div class="result-detail-item">
                    <span class="result-detail-label">邮箱地址</span>
                    <span class="result-detail-value">${escapeHtml(currentEmail)}</span>
                </div>
                ${teamInfo.expires_at ? `
                <div class="result-detail-item">
                    <span class="result-detail-label">到期时间</span>
                    <span class="result-detail-value">${formatDate(teamInfo.expires_at)}</span>
                </div>
                ` : ''}
            </div>

            <p style="color: var(--secondary-color); font-size: 0.9rem; margin-bottom: 1rem;">
                邀请邮件已发送到您的邮箱,请查收并接受邀请。
            </p>

            <button onclick="location.reload()" class="btn btn-primary">
                再次兑换
            </button>
        </div>
    `;

    showStep(3);
}

// 显示错误结果
function showErrorResult(errorMessage) {
    const resultContent = document.getElementById('resultContent');

    resultContent.innerHTML = `
        <div class="result-error">
            <div class="result-icon">❌</div>
            <div class="result-title">兑换失败</div>
            <div class="result-message">${escapeHtml(errorMessage)}</div>

            <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 2rem;">
                <button onclick="backToStep1()" class="btn btn-secondary">
                    返回重试
                </button>
                <button onclick="location.reload()" class="btn btn-primary">
                    重新开始
                </button>
            </div>
        </div>
    `;

    showStep(3);
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '-';

    try {
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    } catch (e) {
        return dateString;
    }
}
