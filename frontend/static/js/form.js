document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contactForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Получаем данные формы
            const formData = {
                name: document.getElementById('name').value,
                phone: document.getElementById('phone').value,
                email: document.getElementById('email').value,
                service: document.getElementById('service').value,
                message: document.getElementById('message').value
            };
            
            // Здесь можно добавить отправку на сервер
            // Пример: fetch('/api/contact', { method: 'POST', body: JSON.stringify(formData) })
            
            // Временное решение - показываем сообщение
            alert('Спасибо за Вашу заявку! Мы свяжемся с Вами в ближайшее время.');
            
            // Очищаем форму
            form.reset();
            
            console.log('Отправлены данные:', formData);
        });
        
        // Маска для телефона
        const phoneInput = document.getElementById('phone');
        if (phoneInput) {
            // Устанавливаем placeholder
            phoneInput.placeholder = '+7 (___) ___-__-__';

            phoneInput.addEventListener('focus', function(e) {
                // При фокусе, если поле пустое, ставим +7
                if (!e.target.value) {
                    e.target.value = '+7 ';
                }
            });

            phoneInput.addEventListener('input', function(e) {
                let value = e.target.value;

                // Сохраняем позицию курсора
                let cursorPosition = e.target.selectionStart;

                // Удаляем все, кроме цифр
                let numbers = value.replace(/\D/g, '');

                // Если первая цифра 8, заменяем на 7
                if (numbers.startsWith('8')) {
                    numbers = '7' + numbers.slice(1);
                }

                // Если не начинается с 7, добавляем
                if (!numbers.startsWith('7')) {
                    numbers = '7' + numbers;
                }

                // Обрезаем до 11 цифр (7 + 10 цифр номера)
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

                // Устанавливаем отформатированное значение
                e.target.value = formatted;

                // Корректируем позицию курсора (упрощённо - ставим в конец)
                // Для более точной позиции нужна сложная логика
                if (cursorPosition < formatted.length) {
                    e.target.setSelectionRange(formatted.length, formatted.length);
                }
            });

            phoneInput.addEventListener('keydown', function(e) {
                // Запрещаем удаление префикса +7
                if ((e.key === 'Backspace' || e.key === 'Delete') &&
                    e.target.selectionStart <= 3) {
                    e.preventDefault();
                }
            });
        }
    }
});
