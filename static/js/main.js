document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Функция для обновления чата в реальном времени
    function updateChat() {
        const chatContainer = document.getElementById('chat-container');
        if (chatContainer) {
            const teamId = chatContainer.dataset.teamId;
            if (teamId) {
                fetch(`/chat/api/messages/${teamId}/`)
                    .then(response => response.json())
                    .then(data => {
                        updateChatMessages(data.messages);
                    })
                    .catch(error => console.error('Error updating chat:', error));
            }
        }
    }
    
    // Обновление сообщений в чате
    function updateChatMessages(messages) {
        const messagesContainer = document.getElementById('messages-container');
        if (!messagesContainer) return;
        
        messagesContainer.innerHTML = '';
        messages.forEach(message => {
            const messageDiv = createMessageElement(message);
            messagesContainer.appendChild(messageDiv);
        });
        
        // Прокрутка к последнему сообщению
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Создание элемента сообщения
    function createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `chat-message ${message.author === currentUserId ? 'own' : 'other'}`;
        div.innerHTML = `
            <div class="message-author">${message.author}</div>
            <div class="message-content">${message.content}</div>
            <div class="message-time">${message.created_at}</div>
        `;
        return div;
    }
    
    // Отправка сообщения
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const contentInput = document.getElementById('message-content');
            const content = contentInput.value.trim();
            
            if (!content) return;
            
            const teamId = messageForm.dataset.teamId;
            
            fetch('/chat/api/send/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    content: content,
                    team_id: teamId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    contentInput.value = '';
                    updateChat();
                } else {
                    alert('Ошибка отправки сообщения: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error sending message:', error);
                alert('Ошибка отправки сообщения');
            });
        });
    }

    // Получение CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Обновление чата каждые 5 секунд
    if (document.getElementById('chat-container')) {
        setInterval(updateChat, 5000);
    }

    // Анимация при загрузке страницы
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(function(element, index) {
        setTimeout(function() {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Копирование текста в буфер обмена
    const copyButtons = document.querySelectorAll('.copy-text');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.text;
            navigator.clipboard.writeText(textToCopy).then(function() {
                showToast('Текст скопирован в буфер обмена');
            });
        });
    });

    // Функция показа уведомлений
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        const container = document.getElementById('toast-container') || createToastContainer();
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
        return container;
    }
});

// Глобальная переменная для имени текущего пользователя
let currentUser = document.querySelector('meta[name="current-user"]')?.content || '';
