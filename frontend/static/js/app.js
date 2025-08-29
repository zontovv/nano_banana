/**
 * GoWombat Doodles Generator - Frontend Application
 */

class DoodleGenerator {
    constructor() {
        this.form = document.getElementById('doodleForm');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingSection = document.getElementById('loadingSection');
        this.resultSection = document.getElementById('resultSection');
        this.errorSection = document.getElementById('errorSection');
        this.resultImage = document.getElementById('resultImage');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newDoodleBtn = document.getElementById('newDoodleBtn');
        this.retryBtn = document.getElementById('retryBtn');
        this.errorMessage = document.getElementById('errorMessage');
        this.generationInfo = document.getElementById('generationInfo');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.downloadBtn.addEventListener('click', () => this.downloadImage());
        this.newDoodleBtn.addEventListener('click', () => this.resetForm());
        this.retryBtn.addEventListener('click', () => this.resetForm());
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        const occasion = document.getElementById('occasion').value.trim();
        const styleHint = document.getElementById('styleHint').value.trim();
        
        if (!occasion) {
            this.showError('Please enter an occasion or event');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/generate-doodle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    occasion: occasion,
                    style_hint: styleHint || null
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please try again later.');
                }
                throw new Error(data.detail || 'Failed to generate doodle');
            }
            
            if (data.success) {
                this.showResult(data);
            } else {
                throw new Error(data.error || 'Failed to generate doodle');
            }
            
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    showLoading() {
        this.form.parentElement.classList.add('hidden');
        this.errorSection.classList.add('hidden');
        this.resultSection.classList.add('hidden');
        this.loadingSection.classList.remove('hidden');
    }
    
    showResult(data) {
        this.loadingSection.classList.add('hidden');
        
        let imageUrl;
        if (data.image_base64) {
            imageUrl = `data:image/png;base64,${data.image_base64}`;
        } else if (data.image_url) {
            imageUrl = data.image_url;
        } else {
            this.showError('No image data received');
            return;
        }
        
        this.resultImage.src = imageUrl;
        this.resultImage.dataset.occasion = data.occasion;
        
        const generationTime = data.generation_time ? data.generation_time.toFixed(2) : 'N/A';
        this.generationInfo.textContent = `Generated in ${generationTime} seconds for: "${data.occasion}"`;
        
        this.resultSection.classList.remove('hidden');
    }
    
    showError(message) {
        this.loadingSection.classList.add('hidden');
        this.resultSection.classList.add('hidden');
        this.form.parentElement.classList.add('hidden');
        
        this.errorMessage.textContent = message;
        this.errorSection.classList.remove('hidden');
    }
    
    resetForm() {
        this.form.reset();
        this.errorSection.classList.add('hidden');
        this.resultSection.classList.add('hidden');
        this.loadingSection.classList.add('hidden');
        this.form.parentElement.classList.remove('hidden');
    }
    
    downloadImage() {
        const imageUrl = this.resultImage.src;
        const occasion = this.resultImage.dataset.occasion || 'doodle';
        
        if (!imageUrl) {
            this.showError('No image to download');
            return;
        }
        
        if (imageUrl.startsWith('data:')) {
            const link = document.createElement('a');
            link.href = imageUrl;
            link.download = `gowombat_${occasion.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            fetch(imageUrl)
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `gowombat_${occasion.replace(/\s+/g, '_').toLowerCase()}_${Date.now()}.png`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                })
                .catch(error => {
                    this.showError('Failed to download image');
                });
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new DoodleGenerator();
});