/**
 * KIM Device Integration - Deep linking and native app features
 */

class DeviceIntegration {
    constructor() {
        this.isNative = this.detectNative();
        this.platform = this.detectPlatform();
        this.availableFeatures = this.detectFeatures();
    }
    
    detectNative() {
        // Check if running in native app wrapper
        return window.nativeBridge !== undefined || 
               navigator.userAgent.includes('KatanxApp') ||
               window.cordova !== undefined ||
               window.Capacitor !== undefined;
    }
    
    detectPlatform() {
        const ua = navigator.userAgent;
        if (/iPad|iPhone|iPod/.test(ua)) {
            return 'ios';
        } else if (/Android/.test(ua)) {
            return 'android';
        }
        return 'web';
    }
    
    detectFeatures() {
        return {
            share: 'share' in navigator,
            contacts: 'contacts' in navigator,
            camera: 'mediaDevices' in navigator && 'getUserMedia' in navigator.mediaDevices,
            photoLibrary: this.platform !== 'web' // Native apps can access photo library
        };
    }
    
    /**
     * Initiate video call - deep link to FaceTime or equivalent
     */
    initiateVideoCall(phoneNumber) {
        if (!phoneNumber) {
            console.error('Phone number required for video call');
            return false;
        }
        
        if (this.platform === 'ios') {
            // Try FaceTime
            const facetimeURL = `facetime://${phoneNumber}`;
            window.location.href = facetimeURL;
            
            // Fallback to WebRTC after timeout
            setTimeout(() => {
                if (!document.hasFocus()) {
                    console.log('FaceTime not available, falling back to WebRTC');
                    this.startWebRTCVideoCall(phoneNumber);
                }
            }, 1000);
            return true;
        } else if (this.platform === 'android') {
            // Android video calling intent
            const intent = `intent://${phoneNumber}#Intent;scheme=tel;action=android.intent.action.CALL;end`;
            window.location.href = intent;
            return true;
        }
        
        // Web fallback - WebRTC
        return this.startWebRTCVideoCall(phoneNumber);
    }
    
    /**
     * Start WebRTC video call (fallback)
     */
    startWebRTCVideoCall(phoneNumber) {
        // In a full implementation, set up WebRTC peer connection
        console.log('Starting WebRTC call to', phoneNumber);
        // TODO: Implement WebRTC signaling
        return false;
    }
    
    /**
     * Open photo editor - deep link to CapCut, VSCO, etc.
     */
    async openPhotoEditor(imageFile) {
        if (this.isNative && window.nativeBridge && window.nativeBridge.openPhotoEditor) {
            return window.nativeBridge.openPhotoEditor(imageFile);
        }
        
        // Try CapCut
        if (this.platform === 'ios' || this.platform === 'android') {
            const capcutURL = `capcut://edit?image=${encodeURIComponent(URL.createObjectURL(imageFile))}`;
            window.location.href = capcutURL;
            
            setTimeout(() => {
                if (!document.hasFocus()) {
                    // Fallback to native share
                    this.shareFile(imageFile, 'Edit Photo');
                }
            }, 1000);
            return true;
        }
        
        // Web fallback - use Canvas API for basic editing
        return this.openWebPhotoEditor(imageFile);
    }
    
    /**
     * Web-based photo editor (fallback)
     */
    openWebPhotoEditor(imageFile) {
        // Basic client-side editing with Canvas API
        console.log('Opening web photo editor for', imageFile.name);
        // TODO: Implement basic web photo editor
        return false;
    }
    
    /**
     * Share file using native share sheet
     */
    async shareFile(file, title = 'Share File') {
        if (!this.availableFeatures.share) {
            console.warn('Native share not available');
            return false;
        }
        
        try {
            if (file instanceof File) {
                await navigator.share({
                    files: [file],
                    title: title
                });
            } else {
                await navigator.share({
                    url: file,
                    title: title
                });
            }
            return true;
        } catch (e) {
            if (e.name !== 'AbortError') {
                console.error('Share failed:', e);
            }
            return false;
        }
    }
    
    /**
     * Initiate phone call
     */
    initiatePhoneCall(phoneNumber) {
        if (!phoneNumber) return false;
        
        const telURL = `tel:${phoneNumber}`;
        window.location.href = telURL;
        return true;
    }
    
    /**
     * Send SMS
     */
    sendSMS(phoneNumber, message = '') {
        if (!phoneNumber) return false;
        
        const smsURL = `sms:${phoneNumber}${message ? `?body=${encodeURIComponent(message)}` : ''}`;
        window.location.href = smsURL;
        return true;
    }
    
    /**
     * Access device photo library (native apps only)
     */
    async accessPhotoLibrary() {
        if (this.isNative && window.nativeBridge && window.nativeBridge.accessPhotoLibrary) {
            return window.nativeBridge.accessPhotoLibrary();
        }
        
        // Web fallback - use file input
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*,video/*';
        input.multiple = false;
        
        return new Promise((resolve) => {
            input.onchange = (e) => {
                resolve(e.target.files[0] || null);
            };
            input.click();
        });
    }
}

// Export for use in other modules
window.DeviceIntegration = DeviceIntegration;

