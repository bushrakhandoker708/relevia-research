// src/components/ChatbotWidget.jsx
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { think } from '../services/releviaBrain';   // ← new brain
import { speak } from '../services/voice';          // ← new voice
import { Heart, X, Send, MessageCircle, Sparkles, Coffee, Minimize2, Maximize2, Volume2, VolumeX, Mic, MicOff } from 'lucide-react';

const Message = ({ message, isBot, isTyping = false, hasError = false, timestamp, isSpeaking }) => {
  const [showTimestamp, setShowTimestamp] = useState(false);
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4 group px-2`}
      onMouseEnter={() => setShowTimestamp(true)}
      onMouseLeave={() => setShowTimestamp(false)}
    >
      <div className={`flex items-start max-w-[85%] sm:max-w-[80%] ${isBot ? 'flex-row' : 'flex-row-reverse'}`}>
        {isBot && (
          <motion.div
            animate={{
              scale: hasError ? [1, 1.05, 1] : isSpeaking ? [1, 1.08, 1] : [1, 1.02, 1],
            }}
            transition={{ duration: hasError ? 1.2 : isSpeaking ? 0.8 : 4, repeat: Infinity, ease: 'easeInOut' }}
            className={`relative w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center mr-2 sm:mr-3 shadow-md ${
              hasError ? 'bg-gradient-to-br from-orange-400 via-orange-500 to-pink-500' : isSpeaking ? 'bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400' : 'bg-gradient-to-br from-purple-400 via-pink-400 to-red-400'
            }`}
          >
            {hasError ? <Coffee className="text-white text-xs sm:text-sm" /> : isSpeaking ? <Volume2 className="text-white text-xs sm:text-sm" /> : <Heart className="text-white text-xs sm:text-sm" />}
            {isSpeaking && <motion.div animate={{ scale: [1, 1.3, 1], opacity: [0.7, 1, 0.7] }} transition={{ duration: 1, repeat: Infinity }} className="absolute inset-0 rounded-full bg-blue-300 opacity-30" />}
          </motion.div>
        )}
        <div className="relative">
          <motion.div whileHover={{ scale: 1.02 }} className={`px-3 sm:px-4 py-3 rounded-2xl shadow-lg backdrop-blur-sm relative overflow-hidden transition-all duration-200 ${isBot ? (hasError ? 'bg-gradient-to-br from-orange-50 to-pink-50 border border-orange-200 text-orange-800' : isSpeaking ? 'bg-gradient-to-br from-blue-50 to-purple-50 border border-blue-200 text-gray-700' : 'bg-gradient-to-br from-white to-purple-50 border border-purple-100 text-gray-700') : 'bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 text-white'}`}>
            {isTyping ? (
              <div className="flex space-x-2 items-center py-1"><span className="text-xs sm:text-sm text-purple-600 mr-2 font-medium">Thinking...</span>{[0, 1, 2].map(i => <motion.div key={i} animate={{ scale: [1, 1.5, 1], opacity: [0.4, 1, 0.4] }} transition={{ duration: 1, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }} className="w-2 h-2 bg-purple-400 rounded-full" />)}<Sparkles className="w-3 h-3 text-purple-400 ml-1" /></div>
            ) : (<p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap font-medium">{message}</p>)}
          </motion.div>
          <AnimatePresence>{showTimestamp && timestamp && (<motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} className={`absolute top-0 ${isBot ? 'left-0' : 'right-0'} text-xs text-gray-400 -mt-5`}>{timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</motion.div>)}</AnimatePresence>
        </div>
        {!isBot && <div className="relative w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-green-400 via-emerald-400 to-teal-500 rounded-full flex items-center justify-center ml-2 sm:ml-3 shadow-md"><span className="text-white text-xs font-bold">You</span></div>}
      </div>
    </motion.div>
  );
};

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [currentlySpeaking, setCurrentlySpeaking] = useState(null);
  const [messages, setMessages] = useState([{ id: 1, text: "Hey there! I'm Relevia—your pocket friend. What's weighing on you?", isBot: true, timestamp: new Date() }]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messageCount, setMessageCount] = useState(0);
  const [userName, setUserName] = useState('');
  const bottomRef = useRef();
  const inputRef = useRef();

  /* ---------- scroll & focus ---------- */
  useEffect(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), [messages]);
  useEffect(() => { if (isOpen && !isMinimized) inputRef.current?.focus(); }, [isOpen, isMinimized]);

  /* ---------- voice ---------- */
  useEffect(() => {
    if (isOpen && voiceEnabled && messages.length === 1) speak(messages[0].text, () => setCurrentlySpeaking(null));
  }, [isOpen, voiceEnabled]);

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
    setCurrentlySpeaking(null);
  };

  /* ---------- send ---------- */
  const handleSend = async () => {
    if (!inputMessage.trim() || isTyping) return;
    if (messageCount >= 12) { // gentle rate-limit
      const gentle = userName
        ? `${userName}, you've shared so much today—let’s pause together. Try 4-7-8 breathing with me?`
        : "Let’s take a gentle breather—4-7-8 breathing together?";
      setMessages(m => [...m, { id: Date.now(), text: gentle, isBot: true, timestamp: new Date(), hasError: true }]);
      if (voiceEnabled) speak(gentle, () => setCurrentlySpeaking(null));
      return;
    }
    const userText = inputMessage.trim();
    setInputMessage('');
    setMessages(m => [...m, { id: Date.now(), text: userText, isBot: false, timestamp: new Date() }]);
    setIsTyping(true);
    setMessageCount(c => c + 1);
    try {
      const reply = await think(userText); // ← on-device brain
      setIsTyping(false);
      setMessages(m => [...m, { id: Date.now() + 1, text: reply, isBot: true, timestamp: new Date() }]);
      if (voiceEnabled) speak(reply, () => setCurrentlySpeaking(null));
    } catch (e) {
      setIsTyping(false);
      const fallback = "I'm having a tiny hiccup—while I fix it, place your hand on your heart and breathe with me.";
      setMessages(m => [...m, { id: Date.now() + 1, text: fallback, isBot: true, timestamp: new Date(), hasError: true }]);
      if (voiceEnabled) speak(fallback, () => setCurrentlySpeaking(null));
    }
  };

  /* ---------- responsive dims ---------- */
  const [isMobile, setIsMobile] = useState(window.innerWidth < 640);
  useEffect(() => { const h = () => setIsMobile(window.innerWidth < 640); window.addEventListener('resize', h); return () => window.removeEventListener('resize', h); }, []);
  const dims = isMobile
    ? { width: 'w-full max-w-sm', height: isMinimized ? 'h-16' : 'h-[500px]', position: 'fixed inset-x-4 bottom-20' }
    : { width: 'w-[420px]', height: isMinimized ? 'h-16' : 'h-[580px]', position: 'fixed left-6 bottom-24' };

  /* ---------- UI ---------- */
  return (
    <>
      {/* launcher */}
      <motion.button
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.4 }}
        onClick={() => setIsOpen(o => !o)}
        className={`${dims.position.split(' ')[0]} left-6 bottom-6 z-50 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-5 py-3 rounded-xl shadow-lg flex items-center gap-2`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isOpen ? <X /> : <MessageCircle />} Relevia
      </motion.button>

      {/* chat window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.9 }}
            className={`${dims.position} ${dims.width} ${dims.height} bg-gradient-to-br from-white via-purple-50/50 to-pink-50/30 backdrop-blur-xl border-2 border-white/60 rounded-2xl shadow-2xl flex flex-col z-50`}
          >
            {/* header */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white p-3 flex items-center justify-between">
              <div className="flex items-center gap-2"><Heart className="w-5 h-5" /><span className="font-semibold">Relevia</span></div>
              <div className="flex items-center gap-2">
                <button onClick={() => setVoiceEnabled(v => !v)}>{voiceEnabled ? <Volume2 /> : <VolumeX />}</button>
                <button onClick={() => setIsMinimized(m => !m)}>{isMinimized ? <Maximize2 /> : <Minimize2 />}</button>
                <button onClick={() => setIsOpen(false)}><X /></button>
              </div>
            </div>

            {/* messages */}
            <AnimatePresence>
              {!isMinimized && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="flex-1 overflow-y-auto p-3 space-y-3">
                  {messages.map(m => <Message key={m.id} message={m.text} isBot={m.isBot} isTyping={false} hasError={m.hasError} timestamp={m.timestamp} isSpeaking={currentlySpeaking === m.id} />)}
                  {isTyping && <Message message="" isBot isTyping />}
                  <div ref={bottomRef} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* input */}
            <AnimatePresence>
              {!isMinimized && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 border-t border-purple-100">
                  <div className="flex gap-2">
                    <input
                      ref={inputRef}
                      value={inputMessage}
                      onChange={e => setInputMessage(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && handleSend()}
                      placeholder={userName ? `What's on your heart, ${userName}?` : "Share what's in your heart..."}
                      className="flex-1 px-3 py-2 border border-purple-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-400"
                    />
                    <button onClick={handleSend} className="p-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"><Send /></button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Not a substitute for professional care • 100 % private</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}