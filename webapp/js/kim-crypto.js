/**
 * KIM Cryptography Module
 * Uses Web Crypto API for ECDH Key Exchange and AES-GCM Encryption
 */

class KIMCrypto {
    constructor() {
        this.keyPair = null;
        this.sharedSecrets = {}; // mapped by userId
        this.publicKeyJWK = null;
        this.dbName = 'kim_crypto_db';
        this.dbVersion = 2; // Incremented to add offlineMessages store
        this.db = null;
        this.initDB();
    }

    /**
     * Initialize IndexedDB for key persistence
     */
    async initDB() {
        if (this.db) return this.db;
        
        return new Promise((resolve, reject) => {
            if (!window.indexedDB) {
                console.warn('IndexedDB not available, key persistence disabled');
                resolve(null);
                return;
            }
            
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onerror = () => {
                const error = request.error;
                // If version error, try to delete and recreate
                if (error && error.name === 'VersionError') {
                    console.warn('IndexedDB version mismatch, deleting and recreating...');
                    const deleteRequest = indexedDB.deleteDatabase(this.dbName);
                    deleteRequest.onsuccess = () => {
                        // Retry opening with correct version
                        const retryRequest = indexedDB.open(this.dbName, this.dbVersion);
                        retryRequest.onsuccess = () => {
                            this.db = retryRequest.result;
                            resolve(this.db);
                        };
                        retryRequest.onerror = () => {
                            console.warn('IndexedDB retry failed:', retryRequest.error);
                            resolve(null);
                        };
                        retryRequest.onupgradeneeded = (event) => {
                            this._createObjectStores(event.target.result);
                        };
                    };
                    deleteRequest.onerror = () => {
                        console.warn('IndexedDB delete failed:', deleteRequest.error);
                        resolve(null);
                    };
                } else {
                    console.warn('IndexedDB open failed:', error);
                    resolve(null); // Don't reject, just disable persistence
                }
            };
            
            request.onsuccess = () => {
                this.db = request.result;
                // Check if we need to upgrade
                if (this.db.version < this.dbVersion) {
                    // Close and reopen with higher version
                    this.db.close();
                    const upgradeRequest = indexedDB.open(this.dbName, this.dbVersion);
                    upgradeRequest.onupgradeneeded = (event) => {
                        this._createObjectStores(event.target.result);
                    };
                    upgradeRequest.onsuccess = () => {
                        this.db = upgradeRequest.result;
                        resolve(this.db);
                    };
                    upgradeRequest.onerror = () => {
                        console.warn('IndexedDB upgrade failed:', upgradeRequest.error);
                        resolve(null);
                    };
                } else {
                    resolve(this.db);
                }
            };
            
            request.onupgradeneeded = (event) => {
                this._createObjectStores(event.target.result);
            };
        });
    }
    
    _createObjectStores(db) {
        if (!db.objectStoreNames.contains('keyPairs')) {
            db.createObjectStore('keyPairs', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('publicKeys')) {
            db.createObjectStore('publicKeys', { keyPath: 'userId' });
        }
        if (!db.objectStoreNames.contains('offlineMessages')) {
            db.createObjectStore('offlineMessages', { keyPath: 'id' });
        }
    }

    /**
     * Save key pair to IndexedDB
     */
    async saveKeyPair() {
        if (!this.db || !this.keyPair || !this.publicKeyJWK) return;
        
        try {
            await this.initDB();
            const tx = this.db.transaction(['keyPairs'], 'readwrite');
            const store = tx.objectStore('keyPairs');
            
            // Export private key (for persistence, we need to store it)
            // Note: In production, consider additional encryption of stored keys
            const privateKeyJWK = await window.crypto.subtle.exportKey(
                'jwk',
                this.keyPair.privateKey
            );
            
            await store.put({
                id: 'current',
                publicKey: this.publicKeyJWK,
                privateKey: privateKeyJWK,
                timestamp: Date.now()
            });
        } catch (e) {
            console.error('Failed to save key pair:', e);
        }
    }

    /**
     * Load key pair from IndexedDB
     */
    async loadKeyPair() {
        if (!this.db) {
            await this.initDB();
        }
        
        if (!this.db) {
            console.warn('IndexedDB not available, cannot load key pair');
            return null;
        }
        
        try {
            const tx = this.db.transaction(['keyPairs'], 'readonly');
            const store = tx.objectStore('keyPairs');
            const request = store.get('current');
            
            return new Promise((resolve, reject) => {
                request.onsuccess = async () => {
                    const data = request.result;
                    if (!data) {
                        resolve(null);
                        return;
                    }
                    
                    try {
                        // Import private key
                        const privateKey = await window.crypto.subtle.importKey(
                            'jwk',
                            data.privateKey,
                            {
                                name: 'ECDH',
                                namedCurve: 'P-256'
                            },
                            false,
                            ['deriveKey', 'deriveBits']
                        );
                        
                        // Import public key
                        const publicKey = await window.crypto.subtle.importKey(
                            'jwk',
                            data.publicKey,
                            {
                                name: 'ECDH',
                                namedCurve: 'P-256'
                            },
                            true,
                            []
                        );
                        
                        // Reconstruct key pair
                        this.keyPair = { privateKey, publicKey };
                        this.publicKeyJWK = data.publicKey;
                        
                        resolve(this.publicKeyJWK);
                    } catch (e) {
                        console.error('Failed to load key pair:', e);
                        resolve(null);
                    }
                };
                
                request.onerror = () => {
                    console.warn('Failed to load key pair from IndexedDB:', request.error);
                    resolve(null); // Don't reject, just return null
                };
            });
        } catch (e) {
            console.error('Failed to load key pair:', e);
            return null;
        }
    }

    /**
     * Save peer public key to IndexedDB
     */
    async savePeerPublicKey(userId, publicKeyJWK) {
        if (!this.db) await this.initDB();
        
        try {
            const tx = this.db.transaction(['publicKeys'], 'readwrite');
            const store = tx.objectStore('publicKeys');
            await store.put({
                userId: userId,
                publicKey: publicKeyJWK,
                timestamp: Date.now()
            });
        } catch (e) {
            console.error('Failed to save peer public key:', e);
        }
    }

    /**
     * Load peer public key from IndexedDB
     */
    async loadPeerPublicKey(userId) {
        if (!this.db) await this.initDB();
        
        try {
            const tx = this.db.transaction(['publicKeys'], 'readonly');
            const store = tx.objectStore('publicKeys');
            const request = store.get(userId);
            
            return new Promise((resolve, reject) => {
                request.onsuccess = () => {
                    const data = request.result;
                    resolve(data ? data.publicKey : null);
                };
                request.onerror = () => reject(request.error);
            });
        } catch (e) {
            console.error('Failed to load peer public key:', e);
            return null;
        }
    }

    /**
     * Generate local ECDH Key Pair (P-256)
     */
    async generateKeyPair() {
        this.keyPair = await window.crypto.subtle.generateKey(
            {
                name: "ECDH",
                namedCurve: "P-256"
            },
            true, // extractable (need to share public key)
            ["deriveKey", "deriveBits"]
        );

        // Export public key for sharing
        this.publicKeyJWK = await window.crypto.subtle.exportKey(
            "jwk",
            this.keyPair.publicKey
        );

        // Save to IndexedDB for persistence
        await this.saveKeyPair();

        return this.publicKeyJWK;
    }

    /**
     * Import a remote user's public key
     */
    async importPeerPublicKey(jwk) {
        return await window.crypto.subtle.importKey(
            "jwk",
            jwk,
            {
                name: "ECDH",
                namedCurve: "P-256"
            },
            true,
            []
        );
    }

    /**
     * Derive shared AES-GCM key from local private key + remote public key
     */
    async deriveSecretKey(peerPublicKey, peerId) {
        if (!this.keyPair) throw new Error("Local key pair not generated");

        const secretKey = await window.crypto.subtle.deriveKey(
            {
                name: "ECDH",
                public: peerPublicKey
            },
            this.keyPair.privateKey,
            {
                name: "AES-GCM",
                length: 256
            },
            false, // key is non-extractable, stays in browser memory
            ["encrypt", "decrypt"]
        );

        this.sharedSecrets[peerId] = secretKey;
        
        // Save peer public key for future use
        const peerPublicKeyJWK = await window.crypto.subtle.exportKey('jwk', peerPublicKey);
        await this.savePeerPublicKey(peerId, peerPublicKeyJWK);
        
        return secretKey;
    }

    /**
     * Encrypt a message
     * Returns: { iv: string(base64), ciphertext: string(base64) }
     */
    async encryptMessage(text, peerId) {
        let key = this.sharedSecrets[peerId];

        // Fallback for global room (mock encryption or derived from a fixed salt for prototype)
        // In real secure chat, group chat requires pairwise keys or Sender Keys (Signal).
        // FOR PROTOTYPE: We will use a temporary "Room Key" derived from room name if peerId is 'global'
        // WARN: This is NOT secure for production global rooms, but sufficient for proving the UI flow.
        if (peerId === 'global') {
            // TODO: Implement proper Group Encryption (Sender Keys)
            // For now, we just pass cleartext labeled as "UNENCRYPTED_GLOBAL"
            // or we derive a weak key just to show the mechanic working differently.
            return {
                iv: null,
                ciphertext: btoa(text),
                mode: 'CLEAR'
            };
        }

        if (!key) throw new Error(`No shared key for ${peerId}`);

        const enc = new TextEncoder();
        const encoded = enc.encode(text);

        // 12 bytes IV for AES-GCM
        const iv = window.crypto.getRandomValues(new Uint8Array(12));

        const ciphertext = await window.crypto.subtle.encrypt(
            {
                name: "AES-GCM",
                iv: iv
            },
            key,
            encoded
        );

        return {
            iv: this.arrayBufferToBase64(iv),
            ciphertext: this.arrayBufferToBase64(ciphertext),
            mode: 'AES-GCM'
        };
    }

    /**
     * Decrypt a message
     */
    async decryptMessage(payload, peerId) {
        if (payload.mode === 'CLEAR') {
            return atob(payload.ciphertext);
        }

        let key = this.sharedSecrets[peerId];
        if (!key) throw new Error(`No shared key for ${peerId}`);

        const iv = this.base64ToArrayBuffer(payload.iv);
        const ciphertext = this.base64ToArrayBuffer(payload.ciphertext);

        try {
            const decrypted = await window.crypto.subtle.decrypt(
                {
                    name: "AES-GCM",
                    iv: iv
                },
                key,
                ciphertext
            );

            const dec = new TextDecoder();
            return dec.decode(decrypted);
        } catch (e) {
            console.error("Decryption failed", e);
            return "[DECRYPTION_FAILURE]";
        }
    }

    // Helpers
    arrayBufferToBase64(buffer) {
        let binary = '';
        const bytes = new Uint8Array(buffer);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary);
    }

    base64ToArrayBuffer(base64) {
        const binary_string = window.atob(base64);
        const len = binary_string.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binary_string.charCodeAt(i);
        }
        return bytes.buffer;
    }
}
