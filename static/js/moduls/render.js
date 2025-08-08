import { BOT_AVATAR, TYPING_INDICATOR, SUGGESTIONS } from './constants.js';
import { saveHistory } from './storage.js';

// Вспомогательная функция: безопасный рендер Markdown/HTML
function renderFormattedText(htmlOrText) {
  // Если есть DOMPurify + marked, используем их
  if (window.marked && typeof window.marked.parse === 'function') {
    const raw = window.marked.parse(htmlOrText);
    if (window.DOMPurify && typeof window.DOMPurify.sanitize === 'function') {
      return window.DOMPurify.sanitize(raw, { USE_PROFILES: { html: true } });
    }
    // fallback — возвращаем raw, но это риск XSS
    return raw;
  }
  // plain text fallback
  const span = document.createElement('span');
  span.textContent = htmlOrText;
  return span.innerHTML;
}

// Создание bubble для одного сообщения
export function createMessageBubble(msg) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble bubble-${msg.who || 'bot'}`;

  if (msg.typing) bubble.setAttribute('data-typing', 'true');
  let innerHTML = '';

  if (msg.who === 'bot') {
    innerHTML += BOT_AVATAR;
  }

  const formatted = renderFormattedText(msg.text || '');

  innerHTML += `<div class="message-content${msg.error ? ' error' : ''}">${formatted}</div>`;

  // Блок оценки — показываем только для сообщений от бота без typing/error и если нет оценки
  if (msg.who === 'bot' && !msg.typing && !msg.error && !msg.user_rating) {
    innerHTML += `
      <div class="message-actions" role="group" aria-label="Оценка ответа">
        <button class="like-btn" data-rating="like" title="Полезный ответ" aria-label="Полезный ответ" aria-pressed="false">
          <span class="material-symbols-outlined">thumb_up</span>
        </button>
        <button class="dislike-btn" data-rating="dislike" title="Неполезный ответ" aria-label="Неполезный ответ" aria-pressed="false">
          <span class="material-symbols-outlined">thumb_down</span>
        </button>
      </div>
    `;
  } else if (msg.who === 'bot' && !msg.typing && !msg.error && msg.user_rating) {
    innerHTML += `<div class="message-rated">${msg.user_rating === 'like' ? '👍 Спасибо!' : '👎 Принято'}</div>`;
  }

  bubble.innerHTML = innerHTML;

  if (msg.who === 'bot' && msg.id) {
    bubble.setAttribute('data-message-id', msg.id);
  }

  return bubble;
}

// Добавить сообщение (или заменить typing)
export function appendMessage(msg, messages, chatHistory, renderMessage) {
  if (msg.replaceTyping) {
    replaceTypingWithAnswer(msg, chatHistory, renderMessage);
    // сохраняем как сообщение от бота
    messages.push({ ...msg, who: 'bot' });
    saveHistory(messages);
  } else {
    renderMessage(msg, chatHistory);
    if (!msg.typing) {
      messages.push(msg);
      saveHistory(messages);
    }
    scrollDown(chatHistory, true);
  }
}

// Заменяет typing bubble на ответ (ищет по DOM)
function replaceTypingWithAnswer(msg, chatHistory, renderMessage) {
  // Ищем bubble, у которого data-typing="true"
  const bubble = chatHistory.querySelector('.chat-bubble.bubble-bot[data-typing="true"]');
  if (bubble) {
    const content = bubble.querySelector('.message-content');
    if (content) {
      // Безопасно рендерим
      if (window.marked && typeof window.marked.parse === 'function') {
        content.innerHTML = renderFormattedText(msg.text || '');
      } else {
        content.textContent = msg.text || '';
      }
      bubble.removeAttribute('data-typing');
      // Добавим data-message-id если есть id
      if (msg.id) bubble.setAttribute('data-message-id', msg.id);
      // Добавляем оценочный блок (если нужно) — проще перерисовать bubble:
      const newBubble = createMessageBubble({ ...msg, who: 'bot' });
      bubble.replaceWith(newBubble);
    }
  } else {
    // Если typing не найден — просто рендерим новое сообщение
    renderMessage(msg, chatHistory);
    scrollDown(chatHistory, true);
  }
}

// Рендер всех сообщений
export function renderAllMessages(messages, chatHistory, renderMessage, renderSuggestions) {
  chatHistory.innerHTML = '';
  (messages || []).forEach(msg => renderMessage(msg, chatHistory));
  scrollDown(chatHistory, false);
  renderSuggestions();
}

// Удалить typing-индикатор
export function removeTyping(chatHistory) {
  // Надёжно: ищем пузырьки с data-typing
  const typingBubbles = chatHistory.querySelectorAll('.chat-bubble[data-typing="true"]');
  typingBubbles.forEach(b => b.remove());
  scrollDown(chatHistory, true);
}

// Рендер одного сообщения (использует createMessageBubble)
export function renderMessage(msg, chatHistory) {
  chatHistory.appendChild(createMessageBubble(msg));
  scrollDown(chatHistory, true);
}

// Тайпинг эффект для ответа бота (можно не использовать, если идёт замена через appendMessage)
export async function typeBotMessage(text, msgmeta, messages, chatHistory) {
  appendMessage({ text, who: 'bot', ...msgmeta, replaceTyping: true }, messages, chatHistory, renderMessage);
}

export function renderSuggestions(messages, suggestionsDiv) {
  if (messages.length === 0) {
    suggestionsDiv.innerHTML = SUGGESTIONS.map(txt => `<button class="suggest-btn">${txt}</button>`).join('');
    suggestionsDiv.style.display = 'block';
  } else {
    suggestionsDiv.style.display = 'none';
  }
}

export function scrollDown(chatHistory, smooth = true) {
  try {
    chatHistory.scrollTo({
      top: chatHistory.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    });
  } catch (err) {
    // fallback
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }
}

// === ЛОГИКА обработки оценки ответов (лайк/дизлайк) ===

export function initRatingHandler(chatHistory, messages) {
  chatHistory.addEventListener('click', async (e) => {
    if (e.target.classList.contains('like-btn') || e.target.classList.contains('dislike-btn')) {
      const button = e.target;
      // Мы должны использовать msg.id, который уже есть в data-message-id
      const msgId = button.closest('.chat-bubble').getAttribute('data-message-id');
      const rating = button.classList.contains('like-btn') ? 'like' : 'dislike';

      if (!msgId) return;

      // Показываем состояние загрузки
      button.style.opacity = '0.5';
      button.disabled = true;

      try {
        const response = await fetch(`/api/rate/${encodeURIComponent(msgId)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ rating })
        });

        const data = await response.json();

        if (data.success) {
          // Обновляем UI - помечаем выбранную кнопку
          const messageDiv = button.closest('.message-actions');
          const likeBtn = messageDiv.querySelector('.like-btn');
          const dislikeBtn = messageDiv.querySelector('.dislike-btn');

          likeBtn.classList.remove('selected', 'like-selected');
          dislikeBtn.classList.remove('selected', 'dislike-selected');

          if (rating === 'like') {
            button.classList.add('selected', 'like-selected');
            button.innerHTML = '👍'; // Или можно оставить иконку из <span class="material-symbols-outlined">thumb_up</span>
          } else {
            button.classList.add('selected', 'dislike-selected');
            button.innerHTML = '👎'; // Или можно оставить иконку из <span class="material-symbols-outlined">thumb_down</span>
          }

          // Показываем анимацию успеха
          button.style.transform = 'scale(1.2)';
          setTimeout(() => {
            button.style.transform = 'scale(1)';
          }, 150);
        } else {
          console.error('Ошибка сервера:', data.error);
          // Показываем ошибку пользователю
          button.innerHTML = '❌';
          setTimeout(() => {
            // Возвращаем исходное состояние иконок
            const originalIcon = rating === 'like' ? '<span class="material-symbols-outlined">thumb_up</span>' : '<span class="material-symbols-outlined">thumb_down</span>';
            button.innerHTML = originalIcon;
          }, 1000);
        }
      } catch (error) {
        console.error('Ошибка при отправке оценки:', error);
        // Показываем ошибку пользователю
        button.innerHTML = '❌';
        setTimeout(() => {
          // Возвращаем исходное состояние иконок
          const originalIcon = rating === 'like' ? '<span class="material-symbols-outlined">thumb_up</span>' : '<span class="material-symbols-outlined">thumb_down</span>';
          button.innerHTML = originalIcon;
        }, 1000);
      } finally {
        button.style.opacity = '1';
        button.disabled = false;
      }
    }
  });
}