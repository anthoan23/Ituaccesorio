// ============================================
// TALLER_CELULAR.JS - Subir fotos desde móvil
// ============================================

// --------------------------------
// 1. CONFIGURACIÓN
// --------------------------------
const CONFIG = {
    API: {
        REGISTRAR_FOTOS: '/api/taller_celular/registrar-fotos'
    },
    MAX_FOTOS: 20,
    MAX_SIZE_MB: 10,
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
};

// --------------------------------
// 2. UTILIDADES
// --------------------------------
const Utils = {
    getCsrfToken() {
        const input = document.querySelector("input[name='_csrf_token']");
        return input?.value || "";
    },

    getAccessToken() {
        return localStorage.getItem("access_token") || 
               localStorage.getItem("token") || 
               sessionStorage.getItem("access_token") || 
               sessionStorage.getItem("token") || 
               "";
    },

    getIdOrden() {
        const input = document.getElementById('orden-id');
        if (input) {
            const id = input.value.trim();
            if (id) {
                console.log('📝 ID de orden obtenido:', id);
                return id;
            }
        }
        
        const urlParts = window.location.pathname.split('/');
        const lastPart = urlParts[urlParts.length - 1];
        if (lastPart && lastPart.startsWith('OS')) {
            console.log('📝 ID de orden obtenido de la URL:', lastPart);
            return lastPart;
        }
        
        console.error('❌ No se pudo obtener el ID de la orden');
        return null;
    },

    escapeHtml(str) {
        if (str === undefined || str === null) return '';
        const text = String(str);
        const div = document.createElement('div');
        div.textContent = text;
        return div.textContent;
    },

    showMessage(message, isError = false) {
        if (!message) return;
        console[isError ? 'error' : 'log'](message);
        const counter = document.getElementById('fotos-counter');
        if (counter) {
            const countSpan = counter.querySelector('#fotos-count');
            const originalText = countSpan ? countSpan.textContent : '0';
            counter.innerHTML = isError ? `❌ ${message}` : `✅ ${message}`;
            counter.style.color = isError ? '#f87171' : '#4ade80';
            setTimeout(() => {
                if (countSpan) {
                    counter.innerHTML = `<span id="fotos-count">${originalText}</span> fotos seleccionadas`;
                } else {
                    counter.innerHTML = `0 fotos seleccionadas`;
                }
                counter.style.color = '';
            }, 3000);
        }
    }
};

// --------------------------------
// 3. GESTOR DE FOTOS
// --------------------------------
const FotoService = {
    fotosSeleccionadas: [],

    getIdOrden() {
        return Utils.getIdOrden();
    },

    abrirSelector() {
        const input = document.getElementById('file-input');
        input.value = '';
        input.click();
    },

    async procesarArchivos(files) {
        const errores = [];
        const archivosValidos = [];

        for (const file of files) {
            if (!CONFIG.ALLOWED_TYPES.includes(file.type)) {
                errores.push(`"${file.name}" - Formato no soportado`);
                continue;
            }

            if (file.size > CONFIG.MAX_SIZE_MB * 1024 * 1024) {
                errores.push(`"${file.name}" - Excede ${CONFIG.MAX_SIZE_MB}MB`);
                continue;
            }

            const existe = this.fotosSeleccionadas.some(f => 
                f.name === file.name && f.size === file.size
            );
            if (existe) {
                errores.push(`"${file.name}" - Ya está en la lista`);
                continue;
            }

            archivosValidos.push(file);
        }

        if (errores.length > 0) {
            errores.forEach(err => Utils.showMessage(err, true));
        }

        if (archivosValidos.length === 0) {
            Utils.showMessage('No hay archivos válidos para agregar', true);
            return;
        }

        const totalFotos = this.fotosSeleccionadas.length + archivosValidos.length;
        if (totalFotos > CONFIG.MAX_FOTOS) {
            Utils.showMessage(`Máximo ${CONFIG.MAX_FOTOS} fotos permitidas`, true);
            return;
        }

        for (const file of archivosValidos) {
            const dataUrl = await this.leerArchivo(file);
            this.fotosSeleccionadas.push({
                name: file.name,
                size: file.size,
                type: file.type,
                dataUrl: dataUrl,
                file: file
            });
        }

        this.renderizarPrevisualizacion();
        this.actualizarContador();
        Utils.showMessage(`${archivosValidos.length} foto(s) agregada(s)`);
    },

    leerArchivo(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(e);
            reader.readAsDataURL(file);
        });
    },

    renderizarPrevisualizacion() {
        const grid = document.getElementById('fotos-preview-grid');

        if (this.fotosSeleccionadas.length === 0) {
            grid.innerHTML = `
                <div class="photos-grid__empty" id="empty-message">
                    <span class="photos-grid__empty-icon">📷</span>
                    <p>Toca para seleccionar fotos</p>
                    <small>Desde tu galería o cámara</small>
                </div>
            `;
            const emptyMsg = document.getElementById('empty-message');
            if (emptyMsg) {
                emptyMsg.addEventListener('click', () => {
                    FotoService.abrirSelector();
                });
            }
            return;
        }

        grid.innerHTML = this.fotosSeleccionadas.map((foto, index) => `
            <div class="photo-item" data-index="${index}">
                <img src="${Utils.escapeHtml(foto.dataUrl)}" alt="Foto ${index + 1}" loading="lazy">
                <button type="button" class="photo-item__remove" data-remover-foto="${index}" aria-label="Quitar foto">
                    ✕
                </button>
            </div>
        `).join('');

        grid.querySelectorAll('.photo-item').forEach(item => {
            const index = parseInt(item.dataset.index);
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.photo-item__remove')) {
                    const foto = FotoService.fotosSeleccionadas[index];
                    if (foto) {
                        FotoService.verFotoAmpliada(foto.dataUrl);
                    }
                }
            });
        });

        grid.querySelectorAll('.photo-item__remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.removerFoto);
                FotoService.eliminarFotoDirecta(index);
            });
        });
    },

    eliminarFotoDirecta(index) {
        if (index === undefined || index === null) return;
        if (index < 0 || index >= this.fotosSeleccionadas.length) return;
        
        const fotoEliminada = this.fotosSeleccionadas[index];
        this.fotosSeleccionadas.splice(index, 1);
        
        if (fotoEliminada) {
            Utils.showMessage(`"${fotoEliminada.name}" removida`);
        }
        
        this.renderizarPrevisualizacion();
        this.actualizarContador();
    },

    actualizarContador() {
        const countEl = document.getElementById('fotos-count');
        if (countEl) {
            countEl.textContent = this.fotosSeleccionadas.length;
        }
        
        const btnSubir = document.getElementById('btn-subir-fotos');
        if (btnSubir) {
            const total = this.fotosSeleccionadas.length;
            btnSubir.disabled = total === 0;
            
            const span = btnSubir.querySelector('span');
            if (span) {
                span.textContent = total === 0 ? 'Subir Fotos' : `Subir ${total} foto${total !== 1 ? 's' : ''}`;
            }
        }
    },

    verFotoAmpliada(dataUrl) {
        const modalImg = document.getElementById('modal-preview-img');
        if (modalImg) {
            modalImg.src = dataUrl;
            if (window.UiModal && typeof window.UiModal.openById === 'function') {
                window.UiModal.openById('modal-photo-preview');
            } else {
                const modal = document.getElementById('modal-photo-preview');
                if (modal) modal.hidden = false;
            }
        }
    },

    async subirFotos() {
        if (this.fotosSeleccionadas.length === 0) {
            Utils.showMessage('No hay fotos para subir', true);
            return;
        }

        const idOrden = this.getIdOrden();
        if (!idOrden) {
            Utils.showMessage('❌ No se encontró el ID de la orden', true);
            return;
        }

        console.log(`📤 Subiendo ${this.fotosSeleccionadas.length} fotos para la orden: ${idOrden}`);

        const progressBar = document.getElementById('upload-progress');
        const progressBarInner = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const btnSubir = document.getElementById('btn-subir-fotos');

        progressBar.hidden = false;
        progressBarInner.style.width = '0%';
        progressText.textContent = 'Preparando...';
        btnSubir.disabled = true;

        try {
            const formData = new FormData();
            formData.append('id_orden', idOrden);
            
            for (const foto of this.fotosSeleccionadas) {
                formData.append('fotos', foto.file);
            }

            const result = await this.enviarConProgreso(formData, progressBarInner, progressText);
            
            Utils.showMessage(`✅ ${result.mensaje || 'Fotos subidas exitosamente'}`);
            
            this.fotosSeleccionadas = [];
            this.renderizarPrevisualizacion();
            this.actualizarContador();

        } catch (error) {
            console.error('Error al subir fotos:', error);
            Utils.showMessage(`❌ Error: ${error.message}`, true);
        } finally {
            progressBar.hidden = true;
            progressBarInner.style.width = '0%';
            btnSubir.disabled = false;
        }
    },

    enviarConProgreso(formData, progressBar, progressText) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBar.style.width = `${percent}%`;
                    progressText.textContent = `Subiendo... ${percent}%`;
                }
            });

            xhr.addEventListener('load', () => {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(response);
                    } else {
                        reject(new Error(response.error || 'Error al subir fotos'));
                    }
                } catch (e) {
                    reject(new Error('Error al procesar la respuesta'));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Error de conexión'));
            });

            xhr.open('POST', CONFIG.API.REGISTRAR_FOTOS);
            
            xhr.setRequestHeader('X-CSRFToken', Utils.getCsrfToken());
            xhr.setRequestHeader('X-CSRF-Token', Utils.getCsrfToken());
            
            const token = Utils.getAccessToken();
            if (token) {
                xhr.setRequestHeader('Authorization', `Bearer ${token}`);
            }
            
            xhr.send(formData);
        });
    }
};

// --------------------------------
// 4. INICIALIZACIÓN Y EVENTOS
// --------------------------------
document.addEventListener('DOMContentLoaded', () => {
    console.log('📱 Taller Celular - Subir fotos');
    
    const idOrden = Utils.getIdOrden();
    if (idOrden) {
        console.log(`✅ Orden #${idOrden} cargada correctamente`);
        const badge = document.querySelector('.orden-badge');
        if (badge) {
            badge.textContent = `Orden #${idOrden}`;
        }
    } else {
        console.warn('⚠️ No se encontró el ID de la orden');
    }

    const btnSubir = document.getElementById('btn-subir-fotos');
    btnSubir.addEventListener('click', () => {
        FotoService.subirFotos();
    });

    const btnAddFotos = document.getElementById('btn-add-fotos');
    if (btnAddFotos) {
        btnAddFotos.addEventListener('click', () => {
            FotoService.abrirSelector();
        });
    }

    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', async (e) => {
        if (e.target.files && e.target.files.length > 0) {
            await FotoService.procesarArchivos(e.target.files);
        }
        e.target.value = '';
    });

    const emptyMsg = document.getElementById('empty-message');
    if (emptyMsg) {
        emptyMsg.addEventListener('click', () => {
            FotoService.abrirSelector();
        });
    }

    const photosGrid = document.getElementById('fotos-preview-grid');
    if (photosGrid) {
        photosGrid.addEventListener('click', (e) => {
            if (e.target === photosGrid || e.target.closest('.photos-grid__empty')) {
                FotoService.abrirSelector();
            }
        });
    }

    document.querySelectorAll('[data-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalPreview = document.getElementById('modal-photo-preview');
            if (modalPreview && !modalPreview.hidden) {
                if (window.UiModal && typeof window.UiModal.close === 'function') {
                    window.UiModal.close();
                } else {
                    modalPreview.hidden = true;
                }
            }
        });
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modalPreview = document.getElementById('modal-photo-preview');
            if (modalPreview && !modalPreview.hidden) {
                if (window.UiModal && typeof window.UiModal.close === 'function') {
                    window.UiModal.close();
                } else {
                    modalPreview.hidden = true;
                }
            }
        }
    });

    FotoService.actualizarContador();
});