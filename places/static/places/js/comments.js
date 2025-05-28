document.addEventListener('DOMContentLoaded', () => {
    console.log('comments.js loaded');

    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!token) {
            console.error('CSRF token not found');
            return null;
        }
        return token.value;
    }

    // Устанавливаем WebSocket-соединение
    const ws = new WebSocket('ws://localhost:8001/ws/posts/');
    ws.onopen = () => console.log('WebSocket connected');
    ws.onerror = (error) => console.error('WebSocket error:', error);
    ws.onclose = (event) => console.log('WebSocket closed:', event);
    ws.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        try {
            const data = JSON.parse(event.data);
            if (data.action === 'like_dislike_update') {
                const update = data.update;
                console.log('Updating post:', update);
                const postDiv = document.querySelector(`.post[data-post-id="${update.post_id}"]`);
                if (postDiv) {
                    const likeCount = postDiv.querySelector('.like-count');
                    const dislikeCount = postDiv.querySelector('.dislike-count');
                    if (likeCount && dislikeCount) {
                        likeCount.textContent = update.likes;
                        dislikeCount.textContent = update.dislikes;
                        console.log(`Updated counts for post ${update.post_id}: likes=${update.likes}, dislikes=${update.dislikes}`);
                    } else {
                        console.error('Like or dislike count elements not found for post', update.post_id);
                    }
                } else {
                    console.error('Post div not found for post', update.post_id);
                }
            }
        } catch (e) {
            console.error('Error parsing WebSocket message:', e);
        }
    };

    // Обработчик кликов по кнопкам лайков и дизлайков
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(button => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const postId = button.dataset.postId;
            const isLike = button.classList.contains('like-btn');
            console.log('Toggling like/dislike for post:', postId, 'isLike:', isLike);

            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                alert('CSRF token not found. Please reload the page.');
                return;
            }

            try {
                const response = await fetch('/places/like_dislike/toggle/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    credentials: 'include', // Убедимся, что куки (включая сессию) отправляются
                    body: JSON.stringify({ post_id: postId, is_like: isLike })
                });

                console.log('Response status:', response.status);
                let data;
                try {
                    data = await response.json();
                } catch (jsonError) {
                    console.error('Failed to parse JSON:', await response.text());
                    throw new Error('Server returned invalid JSON');
                }
                console.log('Like/dislike response:', data);
                if (!response.ok) {
                    throw new Error(data.error || 'Server responded with an error');
                }

                // Немедленное обновление интерфейса
                const postDiv = document.querySelector(`.post[data-post-id="${postId}"]`);
                if (postDiv) {
                    const likeCount = postDiv.querySelector('.like-count');
                    const dislikeCount = postDiv.querySelector('.dislike-count');
                    if (likeCount && dislikeCount) {
                        likeCount.textContent = data.likes;
                        dislikeCount.textContent = data.dislikes;
                        console.log(`Updated local counts for post ${postId}: likes=${data.likes}, dislikes=${data.dislikes}`);
                    }
                }
            } catch (error) {
                console.error('Like/dislike error:', error);
                if (error.message.includes('login')) {
                    alert('Пожалуйста, войдите для установки лайков.');
                } else if (error.message.includes('Forbidden')) {
                    alert('Доступ запрещён. Проверьте авторизацию или обновите страницу.');
                } else {
                    alert('Ошибка при обновлении лайка/дизлайка: ' + error.message);
                }
            }
        });
    });
});