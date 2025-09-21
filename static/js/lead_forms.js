(function () {
  const personTypeSelect = document.querySelector('[data-behaviour="person-type-select"]');
  const personSections = document.querySelectorAll('[data-person-form]');
  const toggleSections = () => {
    if (!personTypeSelect) {
      return;
    }
    const currentType = personTypeSelect.value;
    personSections.forEach((section) => {
      if (section.dataset.personForm === currentType) {
        section.classList.remove('is-hidden');
      } else {
        section.classList.add('is-hidden');
      }
    });
  };

  if (personTypeSelect) {
    personTypeSelect.addEventListener('change', toggleSections);
    toggleSections();
  }

  const lookupButton = document.querySelector('[data-cnpj-lookup]');
  if (!lookupButton) {
    return;
  }

  const feedback = document.querySelector('[data-feedback-target="cnpj"]');
  const fieldMapping = {
    cnpj: 'id_pj-cnpj',
    company_name: 'id_pj-company_name',
    legal_name: 'id_pj-legal_name',
    cep: 'id_pj-cep',
    state: 'id_pj-state',
    city: 'id_pj-city',
    street: 'id_pj-street',
    number: 'id_pj-number',
    complement: 'id_pj-complement',
    neighborhood: 'id_pj-neighborhood',
  };

  const updateFeedback = (message, isError = false) => {
    if (!feedback) {
      return;
    }
    feedback.textContent = message;
    feedback.classList.toggle('error', isError);
  };

  lookupButton.addEventListener('click', async () => {
    const cnpjInput = document.getElementById('id_pj-cnpj');
    if (!cnpjInput) {
      return;
    }

    const cleanedCNPJ = cnpjInput.value.replace(/\D/g, '');
    if (!cleanedCNPJ) {
      updateFeedback('Informe um CNPJ para realizar a consulta.', true);
      return;
    }

    updateFeedback('Consultando a Receita Federal, aguarde...');
    lookupButton.disabled = true;

    try {
      const response = await fetch(`${lookupButton.dataset.cnpjUrl}?cnpj=${encodeURIComponent(cleanedCNPJ)}`);
      const payload = await response.json();

      if (!response.ok) {
        const detail = payload?.detail || 'Não foi possível buscar os dados da Receita Federal.';
        updateFeedback(detail, true);
        return;
      }

      const data = payload.data || {};
      Object.entries(fieldMapping).forEach(([key, fieldId]) => {
        const field = document.getElementById(fieldId);
        if (field && data[key] !== undefined && data[key] !== null) {
          field.value = data[key];
          field.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });

      updateFeedback('Dados preenchidos automaticamente com sucesso. Confira e ajuste se necessário.');
    } catch (error) {
      updateFeedback('Não foi possível completar a consulta. Tente novamente mais tarde.', true);
    } finally {
      lookupButton.disabled = false;
    }
  });
})();
