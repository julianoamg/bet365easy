const BASE_URL = 'https://bot.jacobtips.com';

const iframe = document.createElement('iframe');
iframe.style.display = 'none';


function createLoginBox() {
    const div = document.createElement('div');
    div.id = 'bet365easy-login';

    const baseDiv = document.createElement('div');
    const form = document.createElement('form');

    form.innerHTML = `
            <h1><img src="data:image/png;base64,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"></h1>
            <span id="bet365easy-error"></span>
            <input name="email" type="email" placeholder="E-mail de acesso">
            <input name="password" type="password" placeholder="Senha de acesso">
            <button type="submit">&raquo;</button>
        `;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        e.stopPropagation();

        fetch(BASE_URL + '/login/', {
            method: 'POST',
            body: new FormData(e.target),
        }).then(r => r.json()).then(data => {
            if (data.error) {
                const error = document.getElementById('bet365easy-error');
                error.textContent = data.error;
                error.style.display = 'block';
            }

            if (data.success) {
                div.remove();
                localStorage.bet365easy_sessionid = data.session_id;
                createSendTipButton();
            }
        });
    });

    baseDiv.appendChild(form);
    div.appendChild(baseDiv);

    document.body.appendChild(div);
}

function createSendTipButton() {
    const divButton = document.createElement('div');
    divButton.id = 'bet365easy-sendtip-button';
    const input = document.createElement('input');

    input.placeholder = 'Qtd unidades';
    input.type = 'number';
    input.step = '0.5';
    input.min = '0';
    input.value = localStorage.bet365easy_units || 1;
    input.name = 'units';

    const button = document.createElement('button');
    button.appendChild(input);
    button.id = '';
    button.textContent = 'Enviar Tip';
    button.addEventListener('click', () => {
        button.disabled = true;

        if (!parseFloat(input.value) > 0) {
            alert('Por favor informe o número de únidades antes de enviar a tip.');
            button.disabled = false;
            return;
        }

        const bodyHTML = document.documentElement.innerHTML;

        if (bodyHTML.includes('class="bss-StandardBetslip bss-StandardBetslip-hidden')) {
            alert('A caderneta precisa estar aberta para enviar tips.');
            button.disabled = false;
            return;
        }

        localStorage.bet365easy_units = input.value;

        const body = new FormData();
        body.append('href', location.href);
        body.append('innerHTML', iframe.contentDocument.querySelector.call(document, '.bss-StandardBetslip').outerHTML);
        body.append('betstring', sessionStorage.betstring);
        body.append('units', input.value);

        fetch(BASE_URL + '/send-tip/?session_id=' + localStorage.bet365easy_sessionid, {
            method: 'POST',
            body: body
        }).then(r => r.json()).then(data => {
            if (data.success) {
                alert('Tip enviada com sucesso!');
            }
            if (data.error) {
                alert(data.error);
            }
            button.disabled = false;
        });

        setTimeout(() => {
            button.disabled = false;
        }, 5000);
    });

    document.body.appendChild(iframe);
    divButton.appendChild(input);
    divButton.appendChild(button);
    document.body.append(divButton);
}

fetch(BASE_URL + '/is-authenticated/?session_id=' + localStorage.bet365easy_sessionid).then(r => r.json()).then(data => {
    if (data.error) {
        createLoginBox();
    }
    if (data.success) {
        createSendTipButton();
    }
});
