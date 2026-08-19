(() => {
  // Función para verificar si un elemento está dentro del navbar
  function isInsideNavbar(element) {
    const inDrawerOrTopbar = element.closest('.drawer') !== null || 
                              element.closest('.topbar') !== null;
    
    if (inDrawerOrTopbar && element.closest('#modal-mi-perfil')) {
      return false;
    }
    
    if (element.closest('.user-menu') !== null && !element.closest('#modal-mi-perfil')) {
      return true;
    }
    
    if (element.closest('.notifications') !== null) {
      return true;
    }
    
    return inDrawerOrTopbar;
  }

  const DEFAULT_CONFIG = {
    maxLength: {
      enabled: true,
      showCounter: false,
      showWarning: true,
      warningThreshold: 0.8,
      blockInput: true,
    },
    required: {
      enabled: false,
      showIndicator: true,
      indicatorChar: '*',
    },
    patterns: {
      email: /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/,
      phone: /^[\d\s\-+()]{7,20}$/,
      numeric: /^\d+$/,
      alpha: /^[a-zA-Z\s]+$/,
      alphanumeric: /^[a-zA-Z0-9\s]+$/,
      soloLetras: /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$/,
      soloNumeros: /^\d+$/,
      soloLetrasNumeros: /^[A-Za-z0-9\s]+$/,
      emailSimple: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      url: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
      decimal: /^\d+(\.\d{1,2})?$/,
    },
    liveValidation: true,
    showErrorsInline: true,
    errorClass: 'field-error',
    successClass: 'field-success',
    validationIcons: {
      enabled: true,
      showSuccess: true,
      showError: true,
      showWarning: false,
    },
  };

  const fieldStates = new WeakMap();

  // Reglas predefinidas para bloquear entrada en tiempo real
  const INPUT_FILTER_RULES = {
  noDuplicadoTabla: {
      filter: (value) => value,
      validate: (value, field) => {
        if (!value || !value.trim()) return true;

        const selectorTabla = field.dataset.validarTabla;
        const columnaIndex = parseInt(field.dataset.validarColumna, 10);
        const idInputExclusion = field.dataset.validarExcluirId;

        if (!selectorTabla || !columnaIndex) return true;

        const tbody = document.querySelector(selectorTabla);
        if (!tbody) return true;

        const filas = tbody.querySelectorAll('tr');
        const valorNuevo = value.trim().toLowerCase();

        let idActual = '';
        if (idInputExclusion) {
          const inputId = document.getElementById(idInputExclusion);
          if (inputId) idActual = inputId.value.trim().toLowerCase();
        }

        let duplicado = false;

        filas.forEach(fila => {
          if (fila.querySelector('.table__empty') || fila.querySelector('.table__loading') || fila.querySelector('.table__error')) return;

          const celdaId = fila.querySelector('td:nth-child(1)');
          const celdaNombre = fila.querySelector(`td:nth-child(${columnaIndex})`);

          if (celdaNombre) {
            const textoNombre = celdaNombre.textContent.trim().toLowerCase();
            const textoId = celdaId ? celdaId.textContent.trim().toLowerCase() : '';

            if (textoNombre === valorNuevo) {
              if (idActual && textoId === idActual) return;
              duplicado = true;
            }
          }
        });

        return !duplicado;
      },
      message: 'Este registro ya existe en la tabla actual.'
    },
    
    soloLetras: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\s]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]*$/.test(value),
      message: 'Solo se permiten letras, espacios, acentos y ñ'
    },
    soloNumeros: {
      filter: (value) => value.replace(/[^\d]/g, ''),
      validate: (value) => /^\d*$/.test(value),
      message: 'Solo se permiten números'
    },
    soloLetrasNumeros: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]*$/.test(value),
      message: 'Solo se permiten letras, números y espacios'
    },
    soloLetrasSinEspacios: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ]*$/.test(value),
      message: 'Solo se permiten letras (sin espacios)'
    },
    sinNumeros: {
      filter: (value) => value.replace(/[\d]/g, ''),
      validate: (value) => !/[\d]/.test(value),
      message: 'No se permiten números'
    },
    sinSimbolos: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]*$/.test(value),
      message: 'No se permiten símbolos especiales'
    },
    // Regla específica para nombres de empresas: permite puntos para siglas como "C.A." además de letras, números y espacios
    sinSimbolosEmpresa: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\d\s\.]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s\.]*$/.test(value),
      message: 'No se permiten símbolos especiales, salvo puntos para siglas (ej: C.A.)'
    },
    email: {
      filter: (value) => value.replace(/[^a-zA-Z0-9@._\-]/g, ''),
      validate: (value) => /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/.test(value),
      message: 'Ingrese un correo electrónico válido'
    },
    rif: {
      filter: (value) => value.replace(/[^A-Za-z0-9\-]/g, ''),
      validate: (value) => value === '' || /^[A-Za-z]-?\d{8}-?\d$/.test(value),
      message: 'Ingrese un RIF válido (ej. J-12345678-9)'
    },
    telefono: {
      filter: (value) => value.replace(/[^\d\s\-+()]/g, ''),
      validate: (value) => /^\d{11}$/.test(value.replace(/[\s\-+()]/g, '')),
      message: 'Ingrese un número de teléfono válido (11 dígitos)'
    },
    cedula: {
      filter: (value) => value.replace(/[^\d]/g, ''),
      validate: (value) => /^\d{6,8}$/.test(value),
      message: 'Ingrese una cédula válida (solo números, 6-8 dígitos)'
    },
    sinEspacios: {
      filter: (value) => value.replace(/\s/g, ''),
      validate: (value) => !/\s/.test(value),
      message: 'No se permiten espacios'
    },
    sinCaracteresEspeciales: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s]*$/.test(value),
      message: 'No se permiten caracteres especiales'
    },
    productoNombre: {
      filter: (value) => value.replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñ\d\s\-()]/g, ''),
      validate: (value) => /^[A-Za-zÁÉÍÓÚáéíóúÑñ\d\s\-()]*$/.test(value),
      message: 'Solo se permiten letras, números, espacios, guiones y paréntesis'
    },
    decimal: {
      filter: (value) => {
        let filtered = value.replace(/[^\d.]/g, '');
        const parts = filtered.split('.');
        if (parts.length > 2) {
          filtered = parts[0] + '.' + parts.slice(1).join('');
        }
        if (parts.length === 2 && parts[1].length > 2) {
          filtered = parts[0] + '.' + parts[1].slice(0, 2);
        }
        return filtered;
      },
      validate: (value) => /^\d+(\.\d{1,2})?$/.test(value),
      message: 'Ingrese un número válido (puede incluir hasta 2 decimales)'
    }
  };

  // Reglas predefinidas
  const PREDEFINED_RULES = {
    minLength: (value, min) => value.length >= min,
    maxLength: (value, max) => value.length <= max,
    minValue: (value, min) => parseFloat(value) >= min,
    maxValue: (value, max) => parseFloat(value) <= max,
    email: (value) => /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/.test(value),
    phone: (value) => /^[\d\s\-+()]{7,20}$/.test(value),
    numeric: (value) => /^\d+$/.test(value),
    alpha: (value) => /^[a-zA-Z\s]+$/.test(value),
    alphanumeric: (value) => /^[a-zA-Z0-9\s]+$/.test(value),
    required: (value) => value && value.trim().length > 0,
  };

  class FieldValidator {
    constructor(field, config = {}) {
      this.field = field;
      this.config = this.mergeConfig(config);
      this.counterElement = null;
      this.errorElement = null;
      this.warningElement = null;
      this.validationIcon = null;
      this.iconVisible = false;
      this.initialized = false;
      this.customValidators = [];
      this.inputFilters = [];
      this.touched = false;
      
      this.init();
    }

    mergeConfig(config) {
      let customRules = [];
      if (Array.isArray(config.customRules)) {
        customRules = config.customRules.filter(rule => {
          return rule && typeof rule.validate === 'function';
        });
      }
      
      return {
        maxLength: { ...DEFAULT_CONFIG.maxLength, ...(config.maxLength || {}) },
        required: { ...DEFAULT_CONFIG.required, ...(config.required || {}) },
        patterns: { ...DEFAULT_CONFIG.patterns, ...(config.patterns || {}) },
        liveValidation: config.liveValidation ?? DEFAULT_CONFIG.liveValidation,
        showErrorsInline: config.showErrorsInline ?? DEFAULT_CONFIG.showErrorsInline,
        errorClass: config.errorClass || DEFAULT_CONFIG.errorClass,
        successClass: config.successClass || DEFAULT_CONFIG.successClass,
        validationIcons: { ...DEFAULT_CONFIG.validationIcons, ...(config.validationIcons || {}) },
        customRules: customRules,
        onValidate: config.onValidate || null,
        onLimitReached: config.onLimitReached || null,
        inputFilters: config.inputFilters || [],
      };
    }

    init() {
      if (this.initialized) return;
      
      if (isInsideNavbar(this.field)) {
        return;
      }
      
      this.maxLength = this.getMaxLength();
      this.isRequired = this.field.hasAttribute('required') || this.field.dataset.required === 'true';
      this.pattern = this.field.getAttribute('pattern') || this.field.dataset.pattern;
      this.minLength = this.field.getAttribute('minlength') ? parseInt(this.field.getAttribute('minlength')) : null;
      this.minValue = this.field.getAttribute('min') ? parseFloat(this.field.getAttribute('min')) : null;
      this.maxValue = this.field.getAttribute('max') ? parseFloat(this.field.getAttribute('max')) : null;
      
      this.loadValidationRules();
      
      if (this.config.maxLength.enabled && this.maxLength && !this.field.hasAttribute('maxlength')) {
        this.field.setAttribute('maxlength', this.maxLength);
      }
      
      this.createUI();
      this.bindEvents();
      
      if (this.config.liveValidation) {
        this.validate();
      }
      
      this.initialized = true;
      fieldStates.set(this.field, this);
    }

    loadValidationRules() {
      const rulesAttr = this.field.dataset.validationRules;
      if (rulesAttr) {
        try {
          let rules = [];
          if (rulesAttr.startsWith('{')) {
            const parsed = JSON.parse(rulesAttr);
            rules = Array.isArray(parsed) ? parsed : [parsed];
          } else {
            rules = rulesAttr.split(',').map(r => r.trim());
          }
          
          rules.forEach(rule => {
            if (typeof rule === 'string' && INPUT_FILTER_RULES[rule]) {
              this.inputFilters.push(INPUT_FILTER_RULES[rule]);
            } else if (typeof rule === 'object' && rule.filter) {
              this.inputFilters.push(rule);
            }
          });
        } catch(e) {
          console.warn('Error parsing validation rules:', e);
        }
      }
      
      const filterAttr = this.field.dataset.validationFilter;
      if (filterAttr && INPUT_FILTER_RULES[filterAttr]) {
        this.inputFilters.push(INPUT_FILTER_RULES[filterAttr]);
      }
    }

    getMaxLength() {
      if (this.field.dataset.maxlength) {
        return parseInt(this.field.dataset.maxlength, 10);
      }
      if (this.field.hasAttribute('maxlength')) {
        return parseInt(this.field.getAttribute('maxlength'), 10);
      }
      if (this.config.maxLength.value) {
        return this.config.maxLength.value;
      }
      return null;
    }

    createUI() {
      const wrapper = this.createWrapper();
      
      if (this.config.validationIcons?.enabled !== false) {
        this.validationIcon = this.createValidationIcon();
        if (!this.validationIcon.parentNode) {
          wrapper.appendChild(this.validationIcon);
        }
      }
      
      if (this.config.maxLength.enabled && this.maxLength && this.config.maxLength.showCounter) {
        this.counterElement = this.createCounter();
        if (!this.counterElement.parentNode) {
          wrapper.parentNode.insertBefore(this.counterElement, wrapper.nextSibling);
        }
      }
      
      if (this.config.showErrorsInline) {
        this.errorElement = this.createErrorElement();
        if (!this.errorElement.parentNode) {
          wrapper.parentNode.insertBefore(this.errorElement, wrapper.nextSibling);
        }
      }
      
      if (this.config.maxLength.enabled && this.config.maxLength.showWarning) {
        this.warningElement = this.createWarningElement();
        if (!this.warningElement.parentNode) {
          wrapper.parentNode.insertBefore(this.warningElement, wrapper.nextSibling);
        }
      }
      
      if (this.isRequired && this.config.required.enabled && this.config.required.showIndicator) {
        this.addRequiredIndicator();
      }
    }

    createWrapper() {
      let wrapper = this.field.closest('.field-validator-wrapper');
      
      if (!wrapper) {
        wrapper = document.createElement('div');
        wrapper.className = 'field-validator-wrapper';
        this.field.parentNode.insertBefore(wrapper, this.field);
        wrapper.appendChild(this.field);
      }
      
      return wrapper;
    }

    createValidationIcon() {
      let icon = this.field.parentNode.querySelector('.validation-icon');
      if (!icon) {
        icon = document.createElement('span');
        icon.className = 'validation-icon';
        icon.setAttribute('aria-hidden', 'true');
        icon.style.display = 'none';
      }
      return icon;
    }

    showValidationIcon(type) {
      if (!this.validationIcon) return;
      if (this.config.validationIcons?.enabled === false) return;
      
      if (type === 'success' && !this.config.validationIcons.showSuccess) {
        this.hideValidationIcon();
        return;
      }
      if (type === 'error' && !this.config.validationIcons.showError) {
        this.hideValidationIcon();
        return;
      }
      if (type === 'warning' && !this.config.validationIcons.showWarning) {
        this.hideValidationIcon();
        return;
      }

      const currentType = this.validationIcon.dataset.currentType || '';
      
      // Limpiar clases y estilos
      this.validationIcon.className = 'validation-icon';
      this.validationIcon.style.display = 'flex';
      this.validationIcon.style.background = 'transparent';
      this.validationIcon.style.boxShadow = 'none';
      this.validationIcon.style.borderRadius = '0';
      this.validationIcon.style.padding = '0';
      this.validationIcon.style.width = 'auto';
      this.validationIcon.style.height = 'auto';
      
      const basePath = '/static/img/icons/';
      let imgSrc = '';
      let altText = '';
      
      if (type === 'success') {
        imgSrc = `${basePath}v.png`;
        altText = '✓';
        this.validationIcon.classList.add('success');
      } else if (type === 'error') {
        imgSrc = `${basePath}x.png`;
        altText = '✗';
        this.validationIcon.classList.add('error');
      } else if (type === 'warning') {
        imgSrc = `${basePath}warning.png`;
        altText = '!';
        this.validationIcon.classList.add('warning');
      }
      
      if (imgSrc) {
        this.validationIcon.innerHTML = `
          <img src="${imgSrc}" alt="${altText}" class="validation-icon-img">
        `;
      }
      
      const isSameType = currentType === type;
      const wasVisible = this.iconVisible;
      
      this.validationIcon.dataset.currentType = type;
      
      // Aplicar animación según el estado
      if (!wasVisible) {
        // El icono no estaba visible - aparece con animación de entrada
        this.iconVisible = true;
        requestAnimationFrame(() => {
          this.validationIcon.classList.add('visible', 'icon-appear');
          // Remover la clase después de la animación
          setTimeout(() => {
            this.validationIcon.classList.remove('icon-appear');
          }, 400);
        });
      } else if (!isSameType) {
        // El icono cambió de tipo - animación de cambio
        this.validationIcon.classList.remove('visible');
        // Pequeño delay para la animación de salida
        setTimeout(() => {
          this.iconVisible = true;
          this.validationIcon.classList.add('visible', 'icon-change');
          setTimeout(() => {
            this.validationIcon.classList.remove('icon-change');
          }, 500);
        }, 150);
      } else {
        // Mismo tipo y ya visible - solo asegurar que esté visible
        this.validationIcon.classList.add('visible');
      }
    }

    hideValidationIcon() {
      if (!this.validationIcon) return;
      
      // Animación de salida
      if (this.iconVisible) {
        this.validationIcon.classList.add('icon-hide');
        setTimeout(() => {
          this.iconVisible = false;
          this.validationIcon.classList.remove('visible', 'success', 'error', 'warning', 'icon-hide', 'icon-appear', 'icon-change');
          this.validationIcon.style.display = 'none';
          this.validationIcon.innerHTML = '';
          delete this.validationIcon.dataset.currentType;
        }, 300);
      } else {
        this.iconVisible = false;
        this.validationIcon.classList.remove('visible', 'success', 'error', 'warning');
        this.validationIcon.style.display = 'none';
        this.validationIcon.innerHTML = '';
        delete this.validationIcon.dataset.currentType;
      }
    }

    createCounter() {
      let counter = this.field.parentNode.parentNode ? this.field.parentNode.parentNode.querySelector('.field-counter') : null;
      if (!counter) {
        counter = document.createElement('div');
        counter.className = 'field-counter';
        counter.setAttribute('aria-live', 'polite');
      }
      return counter;
    }

    createErrorElement() {
      let error = this.field.parentNode.parentNode ? this.field.parentNode.parentNode.querySelector('.field-message') : null;
      if (!error) {
        error = document.createElement('div');
        error.className = `field-message ${this.config.errorClass}`;
        error.style.display = 'none';
      }
      return error;
    }

    createWarningElement() {
      let warning = this.field.parentNode.parentNode ? this.field.parentNode.parentNode.querySelector('.field-warning') : null;
      if (!warning) {
        warning = document.createElement('div');
        warning.className = 'field-warning';
        warning.style.display = 'none';
      }
      return warning;
    }

    addRequiredIndicator() {
      const label = this.field.closest('label') || 
                    document.querySelector(`label[for="${this.field.id}"]`);
      
      if (label && !label.querySelector('.required-indicator')) {
        const indicator = document.createElement('span');
        indicator.className = 'required-indicator';
        indicator.textContent = this.config.required.indicatorChar;
        indicator.setAttribute('aria-label', 'Campo requerido');
        label.appendChild(indicator);
      }
    }

    applyInputFilters() {
      if (this.inputFilters.length === 0) return;
      
      let newValue = this.field.value;
      let wasModified = false;
      
      this.inputFilters.forEach(filter => {
        if (filter.filter && typeof filter.filter === 'function') {
          const filtered = filter.filter(newValue);
          if (filtered !== newValue) {
            newValue = filtered;
            wasModified = true;
          }
        }
      });
      
      if (wasModified) {
        const cursorPos = this.field.selectionStart;
        this.field.value = newValue;
        const newPos = Math.min(cursorPos, newValue.length);
        const supportedTypes = ['text', 'search', 'tel', 'url', 'password', 'textarea'];
        if (typeof this.field.setSelectionRange === 'function' && supportedTypes.includes(this.field.type)) {
          try {
            this.field.setSelectionRange(newPos, newPos);
          } catch (e) {
            console.warn('No se pudo ajustar la selección del cursor:', e);
          }
        }
      }
    }
    validateInputFilters() {
      if (this.inputFilters.length === 0) return { valid: true, errors: [] };
      
      let isValid = true;
      const errors = [];
      
      this.inputFilters.forEach(filter => {
        if (filter.validate && typeof filter.validate === 'function') {
          if (!filter.validate(this.field.value, this.field)) {
            isValid = false;
            if (filter.message) {
              errors.push(filter.message);
            }
          }
        }
      });
      
      return { valid: isValid, errors };
    }

    bindEvents() {
      if (this.config.liveValidation) {
        this.field.addEventListener('input', (e) => {
          this.touched = true;
          this.applyInputFilters();
          
          if (this.config.maxLength.enabled && this.config.maxLength.blockInput && this.maxLength) {
            if (this.field.value.length > this.maxLength) {
              this.field.value = this.field.value.slice(0, this.maxLength);
              if (this.config.onLimitReached) {
                this.config.onLimitReached(this.field, this.maxLength);
              }
            }
          }
          
          this.validate();
        });
      }
      
      this.field.addEventListener('blur', () => {
        this.touched = true;
        this.applyInputFilters();
        this.validate(true);
      });
      
      this.field.addEventListener('change', () => {
        this.touched = true;
        this.applyInputFilters();
        this.validate();
      });
    }

    validate(showAllErrors = false) {
      if (showAllErrors) {
        this.touched = true;
      }
      this.isRequired = this.field.hasAttribute('required') || this.field.dataset.required === 'true';
      let isValid = true;
      const errors = [];
      const value = this.field.value;
      const trimmedValue = typeof value === 'string' ? value.trim() : value;
      
      const filterValidation = this.validateInputFilters();
      if (!filterValidation.valid) {
        isValid = false;
        errors.push(...filterValidation.errors);
      }
      
      if (this.isRequired && this.config.required.enabled) {
        if (!trimmedValue || trimmedValue === '') {
          isValid = false;
          errors.push('Este campo es obligatorio.');
        }
      }
      
      if (this.maxLength && this.config.maxLength.enabled && value) {
        if (value.length > this.maxLength) {
          isValid = false;
          errors.push('Máximo ' + this.maxLength + ' caracteres permitidos.');
        }
      }
      
      if (this.minLength && value && value.length < this.minLength) {
        isValid = false;
        errors.push('Mínimo ' + this.minLength + ' caracteres requeridos.');
      }
      
      if (this.pattern && trimmedValue && !this.isRequiredWithEmptyValue()) {
        try {
          const patternRegex = new RegExp(this.pattern);
          if (!patternRegex.test(trimmedValue)) {
            isValid = false;
            errors.push('Formato inválido. Verifique el valor ingresado.');
          }
        } catch (e) {
          console.warn('Invalid pattern:', this.pattern);
        }
      }
      
      const typeValidation = this.validateByType();
      if (!typeValidation.valid) {
        isValid = false;
        errors.push(typeValidation.message);
      }
      
      if (this.minValue !== null && value && !isNaN(parseFloat(value))) {
        if (parseFloat(value) < this.minValue) {
          isValid = false;
          errors.push('El valor mínimo es ' + this.minValue + '.');
        }
      }
      
      if (this.maxValue !== null && value && !isNaN(parseFloat(value))) {
        if (parseFloat(value) > this.maxValue) {
          isValid = false;
          errors.push('El valor máximo es ' + this.maxValue + '.');
        }
      }
      
      if (this.config.customRules && Array.isArray(this.config.customRules)) {
        for (const rule of this.config.customRules) {
          try {
            if (rule.validate && typeof rule.validate === 'function') {
              const result = rule.validate(value, this.field);
              const isValidRule = typeof result === 'boolean' ? result : (result && typeof result.valid === 'boolean' ? result.valid : true);
              const errorMessage = typeof result === 'object' && result.message ? result.message : rule.message;
              
              if (!isValidRule) {
                isValid = false;
                if (errorMessage) {
                  errors.push(errorMessage);
                }
              }
            }
          } catch (e) {
            console.warn('Error in custom rule:', e);
          }
        }
      }
      
      this.showErrors(errors, showAllErrors);
      this.updateFieldStyles(isValid, showAllErrors);
      
      if (this.config.onValidate) {
        this.config.onValidate(this.field, isValid, errors);
      }
      
      return isValid;
    }

    isRequiredWithEmptyValue() {
      return !this.isRequired && (!this.field.value || this.field.value.trim() === '');
    }

    validateByType() {
      const type = this.field.type || this.field.dataset.type;
      const value = this.field.value.trim();
      
      if (!value && !this.isRequired) {
        return { valid: true, message: '' };
      }
      
      switch(type) {
        case 'email':
          if (value && !PREDEFINED_RULES.email(value)) {
            return { valid: false, message: 'Ingrese un correo electrónico válido.' };
          }
          break;
          
        case 'tel':
          if (value && !PREDEFINED_RULES.phone(value)) {
            return { valid: false, message: 'Ingrese un número de teléfono válido.' };
          }
          break;
          
        case 'number':
          if (value && isNaN(Number(value))) {
            return { valid: false, message: 'Ingrese un número válido.' };
          }
          break;
      }
      
      return { valid: true, message: '' };
    }

    showErrors(errors, forceShow = false) {
      if (!this.errorElement) return;
      
      const hasValue = this.field.value && this.field.value.trim() !== '';
      const shouldShow = forceShow || this.touched || this.field.matches(':focus');
      
      if (errors.length > 0 && shouldShow && (forceShow || this.field.matches(':focus') || hasValue)) {
        this.errorElement.textContent = errors.join(' • ');
        this.errorElement.style.display = 'block';
        this.field.setAttribute('aria-invalid', 'true');
        
        if (hasValue) {
          this.showValidationIcon('error');
        } else if (this.field.matches(':focus')) {
          if (this.isRequired && this.config.required.enabled) {
            this.showValidationIcon('warning');
          }
        }
      } else {
        this.errorElement.style.display = 'none';
        this.field.removeAttribute('aria-invalid');
        
        if (shouldShow && hasValue && this.field.value.trim() !== '') {
          this.showValidationIcon('success');
        } else {
          this.hideValidationIcon();
        }
      }
    }

    updateFieldStyles(isValid, forceShow = false) {
      const hasValue = this.field.value && this.field.value.trim() !== '';
      const shouldShow = forceShow || this.touched;
      
      this.field.classList.remove(this.config.errorClass, this.config.successClass);
      
      if (shouldShow) {
        if (isValid && hasValue) {
          this.field.classList.add(this.config.successClass);
          this.showValidationIcon('success');
        } else if (!isValid && hasValue) {
          this.field.classList.add(this.config.errorClass);
          this.showValidationIcon('error');
        } else if (!isValid && this.isRequired && this.config.required.enabled) {
          this.field.classList.add(this.config.errorClass);
          this.showValidationIcon('error');
        } else {
          this.field.classList.remove(this.config.errorClass, this.config.successClass);
          this.hideValidationIcon();
        }
      } else {
        this.field.classList.remove(this.config.errorClass, this.config.successClass);
        this.hideValidationIcon();
      }
    }

    destroy() {
      if (this.counterElement) this.counterElement.remove();
      if (this.errorElement) this.errorElement.remove();
      if (this.warningElement) this.warningElement.remove();
      if (this.validationIcon) this.validationIcon.remove();
      
      const wrapper = this.field.closest('.field-validator-wrapper');
      if (wrapper && wrapper.children.length === 1) {
        wrapper.parentNode.insertBefore(this.field, wrapper);
        wrapper.remove();
      }
      
      const indicator = this.field.closest('label')?.querySelector('.required-indicator');
      if (indicator) indicator.remove();
      
      fieldStates.delete(this.field);
      this.initialized = false;
    }
  }

  function initAllFields() {
    const selectors = [
      'input[type="text"]:not([data-validator-disabled])',
      'input[type="email"]:not([data-validator-disabled])',
      'input[type="password"]:not([data-validator-disabled])',
      'input[type="tel"]:not([data-validator-disabled])',
      'input[type="number"]:not([data-validator-disabled])',
      'input[type="url"]:not([data-validator-disabled])',
      'input[type="search"]:not([data-validator-disabled])',
      'input:not([type]):not([data-validator-disabled])',
      'textarea:not([data-validator-disabled])',
      'select:not([data-validator-disabled])',
    ];
    
    const fields = document.querySelectorAll(selectors.join(','));
    
    fields.forEach((field) => {
      if (isInsideNavbar(field)) {
        return;
      }
      if (fieldStates.has(field)) return;
      if (field.dataset.validator === 'false') return;
      
      const config = getFieldConfig(field);
      try {
        new FieldValidator(field, config);
      } catch (e) {
        console.warn('Error initializing validator for field:', field, e);
      }
    });
  }

  function getFieldConfig(field) {
    const config = {};
    
    if (field.dataset.maxlength) {
      config.maxLength = { value: parseInt(field.dataset.maxlength, 10) };
    }
    
    if (field.dataset.required === 'true') {
      config.required = { enabled: true };
    }
    
    if (field.dataset.pattern) {
      config.patterns = { custom: field.dataset.pattern };
    }
    
    if (field.dataset.validationIcons === 'false') {
      config.validationIcons = { enabled: false };
    }
    
    if (field.dataset.validatorConfig) {
      try {
        const parsed = JSON.parse(field.dataset.validatorConfig);
        if (parsed.customRules && Array.isArray(parsed.customRules)) {
          parsed.customRules = parsed.customRules.filter(rule => {
            return rule && typeof rule.validate === 'function';
          });
        }
        Object.assign(config, parsed);
      } catch(e) {
        console.warn('Error parsing validator config:', e);
      }
    }
    
    return config;
  }

  function validateForm(form, options = {}) {
    const fields = form.querySelectorAll('input, textarea, select');
    let isValid = true;
    const errors = {};
    
    fields.forEach((field) => {
      if (field.disabled || field.type === 'hidden' || field.hidden) {
        return;
      }

      if (field.offsetParent === null) {
        return;
      }

      const style = window.getComputedStyle(field);
      if (style.display === 'none' || style.visibility === 'hidden') {
        return;
      }

      const validator = fieldStates.get(field);
      if (validator) {
        const fieldIsValid = validator.validate(true);
        if (!fieldIsValid) {
          isValid = false;
          errors[field.name || field.id] = {
            element: field,
            valid: false,
          };
        }
      }
    });
    
    if (options.onComplete) {
      options.onComplete(isValid, errors);
    }
    
    return isValid;
  }

  function validateField(field) {
    const validator = fieldStates.get(field);
    if (validator) {
      return validator.validate(true);
    }
    return true;
  }

  function resetForm(form) {
    const fields = form.querySelectorAll('input, textarea, select');
    
    fields.forEach((field) => {
      const validator = fieldStates.get(field);
      if (validator) {
        validator.touched = false;
        field.classList.remove('field-success', 'field-error');
        if (validator.errorElement) {
          validator.errorElement.style.display = 'none';
        }
        if (validator.validationIcon) {
          validator.iconVisible = false;
          validator.validationIcon.className = 'validation-icon';
          validator.validationIcon.style.display = 'none';
          validator.validationIcon.innerHTML = '';
          delete validator.validationIcon.dataset.currentType;
        }
        field.removeAttribute('aria-invalid');
      }
    });
  }

  function initModalFields(modalElement) {
    if (!modalElement) return;
    
    const fields = modalElement.querySelectorAll('input:not([data-validator-disabled]), textarea:not([data-validator-disabled]), select:not([data-validator-disabled])');
    
    fields.forEach((field) => {
      if (!fieldStates.has(field) && field.dataset.validator !== 'false') {
        const config = getFieldConfig(field);
        try {
          new FieldValidator(field, config);
        } catch (e) {
          console.warn('Error initializing validator for modal field:', field, e);
        }
      }
    });
  }

  const modalObserver = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
        const modal = mutation.target;
        if (modal.classList && modal.classList.contains('ui-modal') && modal.style.display !== 'none') {
          setTimeout(() => initModalFields(modal), 50);
        }
      }
      
      if (mutation.type === 'childList' && mutation.addedNodes.length) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.classList && node.classList.contains('ui-modal')) {
              if (node.style.display !== 'none') {
                setTimeout(() => initModalFields(node), 50);
              }
            }
            
            if (node.matches && (node.matches('input, textarea, select'))) {
              if (!isInsideNavbar(node)) {
                setTimeout(() => {
                  if (!fieldStates.has(node) && node.dataset.validator !== 'false') {
                    const config = getFieldConfig(node);
                    try {
                      new FieldValidator(node, config);
                    } catch(e) {}
                  }
                }, 50);
              }
            }
          }
        }
      }
    }
  });
  
  modalObserver.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['style', 'class']
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllFields);
  } else {
    initAllFields();
  }

  window.FieldValidator = {
    init: initAllFields,
    validateForm: validateForm,
    validateField: validateField,
    resetForm: resetForm,
    initModalFields: initModalFields,
    FieldValidator: FieldValidator,
    addFilterRule: (name, rule) => { INPUT_FILTER_RULES[name] = rule; },
    getFilterRules: () => ({ ...INPUT_FILTER_RULES }),
  };
})();