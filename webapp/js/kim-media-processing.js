/**
 * KIM Media Processing - Client-side compression and optimization
 */

class MediaProcessor {
    constructor() {
        this.workers = new Map();
    }
    
    /**
     * Compress image before upload
     */
    async compressImage(file, maxWidth = 1920, quality = 0.8) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = new Image();
                
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    // Calculate new dimensions
                    let width = img.width;
                    let height = img.height;
                    
                    if (width > maxWidth) {
                        height = (height * maxWidth) / width;
                        width = maxWidth;
                    }
                    
                    canvas.width = width;
                    canvas.height = height;
                    
                    // Draw and compress
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    // Convert to blob with compression
                    canvas.toBlob(
                        (blob) => {
                            if (blob) {
                                resolve(blob);
                            } else {
                                reject(new Error('Compression failed'));
                            }
                        },
                        'image/jpeg',
                        quality
                    );
                };
                
                img.onerror = () => reject(new Error('Image load failed'));
                img.src = e.target.result;
            };
            
            reader.onerror = () => reject(new Error('File read failed'));
            reader.readAsDataURL(file);
        });
    }
    
    /**
     * Generate thumbnail for image
     */
    async generateThumbnail(file, maxSize = 200) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const img = new Image();
                
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    // Calculate thumbnail dimensions
                    let width = img.width;
                    let height = img.height;
                    
                    if (width > height) {
                        if (width > maxSize) {
                            height = (height * maxSize) / width;
                            width = maxSize;
                        }
                    } else {
                        if (height > maxSize) {
                            width = (width * maxSize) / height;
                            height = maxSize;
                        }
                    }
                    
                    canvas.width = width;
                    canvas.height = height;
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    canvas.toBlob(
                        (blob) => {
                            if (blob) {
                                resolve(blob);
                            } else {
                                reject(new Error('Thumbnail generation failed'));
                            }
                        },
                        'image/jpeg',
                        0.7
                    );
                };
                
                img.onerror = () => reject(new Error('Image load failed'));
                img.src = e.target.result;
            };
            
            reader.onerror = () => reject(new Error('File read failed'));
            reader.readAsDataURL(file);
        });
    }
    
    /**
     * Compress video (basic - uses MediaRecorder API)
     */
    async compressVideo(file, maxBitrate = 2000000) {
        return new Promise((resolve, reject) => {
            const video = document.createElement('video');
            video.preload = 'metadata';
            
            video.onloadedmetadata = () => {
                video.currentTime = 0.01; // Seek to first frame
            };
            
            video.onloadeddata = () => {
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                
                // Draw first frame to get dimensions
                ctx.drawImage(video, 0, 0);
                
                // Use MediaRecorder for compression
                const stream = canvas.captureStream();
                const mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'video/webm;codecs=vp9',
                    videoBitsPerSecond: maxBitrate
                });
                
                const chunks = [];
                mediaRecorder.ondataavailable = (e) => {
                    if (e.data.size > 0) {
                        chunks.push(e.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    const blob = new Blob(chunks, { type: 'video/webm' });
                    resolve(blob);
                };
                
                mediaRecorder.start();
                video.play();
                
                setTimeout(() => {
                    mediaRecorder.stop();
                    video.pause();
                }, 100);
            };
            
            video.onerror = () => reject(new Error('Video load failed'));
            video.src = URL.createObjectURL(file);
        });
    }
    
    /**
     * Process file - compress if needed
     */
    async processFile(file, options = {}) {
        const {
            compressImages = true,
            maxImageWidth = 1920,
            imageQuality = 0.8,
            compressVideos = false,
            generateThumbnails = true
        } = options;
        
        const fileType = file.type.split('/')[0];
        let processedFile = file;
        let thumbnail = null;
        
        try {
            if (fileType === 'image' && compressImages) {
                processedFile = await this.compressImage(file, maxImageWidth, imageQuality);
                
                if (generateThumbnails) {
                    thumbnail = await this.generateThumbnail(file);
                }
            } else if (fileType === 'video' && compressVideos) {
                // Video compression is more complex, skip for now
                // processedFile = await this.compressVideo(file);
            }
            
            return {
                file: processedFile,
                thumbnail: thumbnail,
                originalSize: file.size,
                processedSize: processedFile.size,
                saved: file.size - processedFile.size
            };
        } catch (e) {
            console.error('File processing error:', e);
            // Return original file if processing fails
            return {
                file: file,
                thumbnail: null,
                originalSize: file.size,
                processedSize: file.size,
                saved: 0
            };
        }
    }
}

// Export for use
window.MediaProcessor = MediaProcessor;

