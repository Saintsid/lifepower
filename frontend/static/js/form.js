document.addEventListener('DOMContentLoaded', function() {
    console.log('form.js loaded'); // Для отладки

    // Обработчик формы контакта/записи
    const form = document.getElementById('contactForm');

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Получаем данные формы
            const formData = {
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                email: document.getElementById('email').value,
                service: document.getElementById('service')?.value,
                message: document.getElementById('message')?.value
            };

            // Здесь можно добавить отправку на сервер
            // Пример: fetch('/api/contact', { method: 'POST', body: JSON.stringify(formData) })

            // Временное решение - показываем сообщение
            alert('Спасибо за Вашу заявку! Мы свяжемся с Вами в ближайшее время.');

            // Очищаем форму
            form.reset();

            console.log('Отправлены данные:', formData);
        });
    }

    // Маска для телефона - применяется ко ВСЕМ полям с id="phone"
    const phoneInputs = document.querySelectorAll('input[type="tel"], #phone');

    phoneInputs.forEach(function(phoneInput) {
        console.log('Phone input found:', phoneInput); // Для отладки

        // Устанавливаем placeholder
        if (!phoneInput.placeholder || phoneInput.placeholder === '') {
            phoneInput.placeholder = '+7 (___) ___-__-__';
        }

        // При фокусе устанавливаем +7 если пустое
        phoneInput.addEventListener('focus', function(e) {
            if (!e.target.value || e.target.value === '') {
                e.target.value = '+7 ';
                // Ставим курсор после +7
                setTimeout(() => {
                    e.target.setSelectionRange(3, 3);
                }, 0);
            }
        });

        // Форматирование при вводе
        phoneInput.addEventListener('input', function(e) {
            let value = e.target.value;

            // Удаляем все, кроме цифр
            let numbers = value.replace(/\D/g, '');

            // Если пользователь пытается удалить всё - оставляем +7
            if (numbers === '' || numbers === '7') {
                e.target.value = '+7 ';
                e.target.setSelectionRange(3, 3);
                return;
            }

            // Если первая цифра 8, заменяем на 7
            if (numbers.startsWith('8')) {
                numbers = '7' + numbers.slice(1);
            }

            // Если не начинается с 7, добавляем
            if (!numbers.startsWith('7')) {
                numbers = '7' + numbers;
            }

            // Обрезаем до 11 цифр
            numbers = numbers.slice(0, 11);

            // Форматируем
            let formatted = '+7';

            if (numbers.length > 1) {
                formatted += ' (' + numbers.slice(1, 4);
            }
            if (numbers.length >= 5) {
                formatted += ') ' + numbers.slice(4, 7);
            }
            if (numbers.length >= 8) {
                formatted += '-' + numbers.slice(7, 9);
            }
            if (numbers.length >= 10) {
                formatted += '-' + numbers.slice(9, 11);
            }

            e.target.value = formatted;
        });

        // Запрет удаления +7
        phoneInput.addEventListener('keydown', function(e) {
            const cursorPos = e.target.selectionStart;
            const value = e.target.value;

            // Если пытаются удалить +7 или пробел после него
            if ((e.key === 'Backspace' || e.key === 'Delete') && cursorPos <= 3) {
                e.preventDefault();
                return false;
            }

            // Если поле пустое или только +7, не даём полностью очистить
            if ((e.key === 'Backspace' || e.key === 'Delete') &&
                (value === '+7 ' || value === '+7')) {
                e.preventDefault();
                return false;
            }
        });

        // Запрет вставки некорректных данных
        phoneInput.addEventListener('paste', function(e) {
            e.preventDefault();

            // Получаем текст из буфера
            const pasteData = (e.clipboardData || window.clipboardData).getData('text');

            // Извлекаем только цифры
            const numbers = pasteData.replace(/\D/g, '');

            if (numbers.length > 0) {
                // Симулируем ввод цифр
                const event = new Event('input', { bubbles: true });
                e.target.value = numbers;
                e.target.dispatchEvent(event);
            }
        });
    });
});
