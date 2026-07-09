import React, { useState, useEffect } from 'react';
import useNotifications from '../../hooks/useNotifications';

export default function TelegramLinkSettings() {
  const { 
    telegramStatus, 
    fetchTelegramStatus, 
    linkTelegram, 
    verifyTelegram, 
    unlinkTelegram, 
    loading, 
    error 
  } = useNotifications();
  
  const [chatIdInput, setChatIdInput] = useState('');
  const [verifyCodeInput, setVerifyCodeInput] = useState('');
  const [isLinking, setIsLinking] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Fetch status on mount
  useEffect(() => {
    fetchTelegramStatus();
  }, [fetchTelegramStatus]);

  const handleLink = async (e) => {
    e.preventDefault();
    if (!chatIdInput.trim()) return;
    
    setIsLinking(true);
    setSuccessMsg('');
    const success = await linkTelegram(chatIdInput.trim());
    setIsLinking(false);
    
    if (success) {
      setSuccessMsg('Link initiated! Enter code below to verify.');
      setChatIdInput('');
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!verifyCodeInput.trim()) return;
    
    setIsVerifying(true);
    setSuccessMsg('');
    const success = await verifyTelegram(verifyCodeInput.trim());
    setIsVerifying(false);
    
    if (success) {
      setSuccessMsg('Telegram verified and active!');
      setVerifyCodeInput('');
    }
  };

  const handleUnlink = async () => {
    if (window.confirm('Are you sure you want to disable Telegram notifications and unlink your account?')) {
      const success = await unlinkTelegram();
      if (success) {
        setSuccessMsg('Telegram unlinked successfully.');
        setTimeout(() => setSuccessMsg(''), 3000);
      }
    }
  };

  if (!telegramStatus) {
    return (
      <div 
        className="bg-[#16161C] border border-[#8A8A97]/15 rounded-xl p-5 text-[#8A8A97] max-w-md w-full text-center text-xs"
        style={{ boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)' }}
      >
        Loading Telegram Settings...
      </div>
    );
  }

  const isLinked = telegramStatus.linked || (telegramStatus.chatId && telegramStatus.isVerified);

  return (
    <div
      className="bg-[#16161C] border border-[#8A8A97]/15 rounded-xl p-5 text-[#F4F4F7] max-w-md w-full"
      style={{
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
      }}
    >
      {/* Title */}
      <div className="flex items-center gap-3 border-b border-[#8A8A97]/10 pb-4 mb-4">
        {/* Telegram Icon */}
        <div className="w-8 h-8 rounded-lg bg-[#18E7FF]/10 flex items-center justify-center text-[#18E7FF]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </div>
        <div>
          <h4 className="font-bold text-sm tracking-wide">TELEGRAM NOTIFICATIONS</h4>
          <p className="text-[10px] text-[#8A8A97]">Get instant order updates directly on your chat</p>
        </div>
      </div>

      {/* Main Status Router */}
      {isLinked ? (
        // STATE 1: Subscribed & Active
        <div className="space-y-4">
          <div className="bg-[#18E7FF]/5 border border-[#18E7FF]/30 rounded-lg p-4 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-[10px] uppercase font-bold text-[#18E7FF] tracking-wider block">
                Status: ACTIVE & VERIFIED
              </span>
              <p className="text-xs font-mono text-[#F4F4F7]">
                Chat ID: {telegramStatus.chatId}
              </p>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-[#18E7FF] animate-pulse"></span>
          </div>

          <p className="text-xs text-[#8A8A97] leading-relaxed">
            Your account is verified. You will receive in-app alerts on Telegram alongside In-App notifications.
          </p>

          <button
            onClick={handleUnlink}
            disabled={loading}
            className="w-full py-2 bg-[#FF2E8A]/10 border border-[#FF2E8A]/30 text-[#FF2E8A] hover:bg-[#FF2E8A] hover:text-white rounded-lg text-xs font-semibold transition-all duration-300 shadow-sm focus:outline-none"
          >
            Unlink Telegram Account
          </button>
        </div>
      ) : telegramStatus.chatId ? (
        // STATE 2: Pending Verification
        <div className="space-y-4">
          <div className="bg-[#FFD84D]/5 border border-[#FFD84D]/30 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-bold text-[#FFD84D] tracking-wider block">
                Status: PENDING VERIFICATION
              </span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#FFD84D] animate-pulse"></span>
            </div>
            <p className="text-[11px] text-[#8A8A97] leading-relaxed">
              Verify ownership of Chat ID <strong className="text-[#F4F4F7] font-mono">{telegramStatus.chatId}</strong>. 
              We have sent a verification code to your Telegram chat via <strong className="text-[#18E7FF]">@GALXY_Alerts_Bot</strong>. Enter that code below to complete verification:
            </p>


            <form onSubmit={handleVerify} className="space-y-2 pt-2">
              <div className="space-y-1">
                <input
                  type="text"
                  value={verifyCodeInput}
                  onChange={(e) => setVerifyCodeInput(e.target.value.replace(/\D/g, '').substring(0, 6))}
                  placeholder="Enter 6-digit code"
                  className="w-full bg-[#0B0B0F] border border-[#8A8A97]/20 rounded-lg px-3 py-2 text-xs text-center text-[#F4F4F7] placeholder-[#8A8A97]/40 focus:border-[#FFD84D] focus:outline-none transition-all duration-200"
                />
              </div>

              <button
                type="submit"
                disabled={isVerifying || verifyCodeInput.length !== 6}
                className="w-full py-2 bg-[#FFD84D] hover:bg-[#FFD84D]/85 disabled:opacity-40 text-black font-bold rounded-lg text-xs tracking-wide transition-all duration-300 focus:outline-none"
              >
                {isVerifying ? 'Verifying...' : 'Verify Ownership'}
              </button>
            </form>

            <button
              onClick={unlinkTelegram}
              className="w-full py-1 text-center text-[10px] text-[#FF2E8A] hover:underline bg-transparent border-0 cursor-pointer"
            >
              Cancel Link & Try Another ID
            </button>
          </div>
        </div>
      ) : (
        // STATE 3: Unlinked Setup
        <div className="space-y-4">
          {/* Setup Guide */}
          <div className="bg-[#0B0B0F]/50 border border-[#8A8A97]/10 rounded-lg p-4 space-y-2.5">
            <span className="text-[10px] uppercase font-bold text-[#9B5CFF] tracking-wider block">
              SETUP INSTRUCTIONS
            </span>
            <ol className="list-decimal list-inside text-xs text-[#8A8A97] space-y-1.5 leading-relaxed">
              <li>
                Open Telegram and search for <strong className="text-[#F4F4F7] font-semibold">@GALXY_Alerts_Bot</strong>.
              </li>
              <li>
                Send the command <code className="bg-[#16161C] px-1.5 py-0.5 rounded text-[#18E7FF] font-mono">/start</code>.
              </li>
              <li>
                The bot will reply with your unique 9 or 10-digit <strong className="text-[#F4F4F7] font-semibold">Telegram Chat ID</strong>.
              </li>
              <li>
                Copy the ID and enter it in the form below.
              </li>
            </ol>
          </div>

          {/* Setup Form */}
          <form onSubmit={handleLink} className="space-y-3">
            <div className="space-y-1">
              <label htmlFor="chatId" className="text-[10px] text-[#8A8A97] uppercase tracking-wider font-semibold block">
                Telegram Chat ID
              </label>
              <input
                id="chatId"
                type="text"
                value={chatIdInput}
                onChange={(e) => setChatIdInput(e.target.value.replace(/\D/g, ''))} // numeric only
                placeholder="e.g. 581290382"
                className="w-full bg-[#0B0B0F] border border-[#8A8A97]/20 rounded-lg px-3 py-2 text-xs text-[#F4F4F7] placeholder-[#8A8A97]/40 focus:border-[#9B5CFF] focus:outline-none focus:ring-1 focus:ring-[#9B5CFF] transition-all duration-200"
                style={{
                  boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.5)'
                }}
              />
            </div>

            <button
              type="submit"
              disabled={isLinking || !chatIdInput.trim()}
              className="w-full py-2 bg-[#9B5CFF] hover:bg-[#9B5CFF]/85 disabled:opacity-40 disabled:hover:bg-[#9B5CFF] text-white rounded-lg text-xs font-semibold tracking-wide transition-all duration-300 focus:outline-none"
              style={{
                boxShadow: chatIdInput.trim() ? '0 0 10px rgba(155, 92, 255, 0.4)' : 'none'
              }}
            >
              {isLinking ? 'Linking Account...' : 'Link Telegram'}
            </button>
          </form>
        </div>
      )}

      {/* Status Messages */}
      {successMsg && (
        <div className="mt-3 text-center text-xs text-[#18E7FF] font-medium animate-pulse">
          {successMsg}
        </div>
      )}
      {error && (
        <div className="mt-3 text-center text-xs text-[#FF2E8A] font-medium">
          Error: {error}
        </div>
      )}
    </div>
  );
}
