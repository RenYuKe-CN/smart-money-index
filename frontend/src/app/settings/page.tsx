"use client";
import { useState, useEffect } from "react";
import { Key, CheckCircle, XCircle, Save, Loader2, ArrowLeft, Bot } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function SettingsPage() {
  var [clawbyKey, setClawbyKey] = useState("");
  var [configured, setConfigured] = useState(false);
  var [preview, setPreview] = useState("");
  var [saving, setSaving] = useState(false);
  var [status, setStatus] = useState("");
  var [llmProviderType, setLlmProviderType] = useState("openai");
  var [llmApiBase, setLlmApiBase] = useState("https://api.openai.com/v1");
  var [llmApiKey, setLlmApiKey] = useState("");
  var [llmModel, setLlmModel] = useState("gpt-4o");
  var [llmConfigured, setLlmConfigured] = useState(false);
  var [llmSaving, setLlmSaving] = useState(false);
  var [llmStatus, setLlmStatus] = useState("");

  useEffect(function() {
    api.config().then(function(c) {
      setConfigured(c.clawby_configured);
      setPreview(c.api_key_preview || "");
    }).catch(function() {});
    api.llmConfig().then(function(l) {
      if (l.provider_type) setLlmProviderType(l.provider_type);
      if (l.api_base) setLlmApiBase(l.api_base);
      if (l.model) setLlmModel(l.model);
      setLlmConfigured(l.configured);
    }).catch(function() {});
  }, []);

  function handleSaveLlm() {
    setLlmSaving(true);
    api.updateLlmConfig({
      llm_provider_type: llmProviderType,
      llm_api_base: llmApiBase,
      llm_api_key: llmApiKey || undefined,
      llm_model: llmModel,
    }).then(function() {
      setLlmStatus("LLM 配置已保存");
      setLlmApiKey("");
      setLlmConfigured(true);
    }).catch(function(err) {
      setLlmStatus("保存失败: " + String(err));
    }).finally(function() {
      setLlmSaving(false);
    });
  }

  function handleSave() {
    if (!clawbyKey.trim()) return;
    setSaving(true);
    api.updateClawbyKey(clawbyKey.trim()).then(function() {
      setStatus("已保存");
      setClawbyKey("");
      return api.config();
    }).then(function(c) {
      setConfigured(c.clawby_configured);
      setPreview(c.api_key_preview || "");
    }).catch(function(err) {
      setStatus(String(err));
    }).finally(function() {
      setSaving(false);
    });
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <Link href="/" className="btn-secondary px-3 py-1.5 text-sm flex items-center gap-1">
            <ArrowLeft size={16} /> 返回
          </Link>
          <h1 className="text-lg font-semibold text-[#e2e8f0]">设置</h1>
        </div>
        <div className="card p-5 space-y-4">
          <h2 className="text-sm font-medium text-[#e2e8f0] flex items-center gap-2">
            <Key size={16} /> Clawby API Key
          </h2>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-[#7c8db5]">状态:</span>
            {configured ? (
              <span className="flex items-center gap-1 text-[#26a69a]">
                <CheckCircle size={14} /> 已配置
                {preview && <span className="text-xs text-[#4a5568]">({preview})</span>}
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[#ef5350]">
                <XCircle size={14} /> 未配置
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <input type="password" value={clawbyKey}
              onChange={function(e) { setClawbyKey(e.target.value); }}
              placeholder="输入 Clawby API Key (pk...)"
              className="flex-1 bg-[#1a1d2e] border border-[#2d3748] rounded px-3 py-2 text-sm text-[#e2e8f0]" />
            <button onClick={handleSave} disabled={saving || !clawbyKey.trim()}
              className="btn-primary flex items-center gap-1.5 text-sm px-4">
              {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />} 保存
            </button>
          </div>
          {status && <p className="text-xs text-[#7c8db5]">{status}</p>}
          <p className="text-xs text-[#4a5568]">
            免费注册: <a href="https://www.openclawby.com/" target="_blank" className="text-[#3b82f6] hover:underline">openclawby.com</a>
          </p>
        </div>
        <div className="card p-5 space-y-4">
          <h2 className="text-sm font-medium text-[#e2e8f0] flex items-center gap-2">
            <Bot size={16} /> LLM Provider
          </h2>
          <div className="flex items-center gap-2 text-sm">
            <span className="text-[#7c8db5]">状态:</span>
            {llmConfigured ? (
              <span className="flex items-center gap-1 text-[#26a69a]"><CheckCircle size={14} /> 已配置</span>
            ) : (
              <span className="flex items-center gap-1 text-[#ef5350]"><XCircle size={14} /> 未配置</span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-[#7c8db5]">Provider 类型</label>
              <select value={llmProviderType} onChange={function(e) { setLlmProviderType(e.target.value); }}
                className="w-full bg-[#1a1d2e] border border-[#2d3748] rounded px-3 py-2 text-sm text-[#e2e8f0] mt-1">
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="custom_openai">自定义 (OpenAI 兼容)</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-[#7c8db5]">默认模型</label>
              <input value={llmModel} onChange={function(e) { setLlmModel(e.target.value); }}
                type="text" placeholder="gpt-4o"
                className="w-full bg-[#1a1d2e] border border-[#2d3748] rounded px-3 py-2 text-sm text-[#e2e8f0] mt-1" />
            </div>
          </div>
          <div>
            <label className="text-xs text-[#7c8db5]">API Base URL</label>
            <input value={llmApiBase} onChange={function(e) { setLlmApiBase(e.target.value); }}
              type="text" placeholder="https://api.openai.com/v1"
              className="w-full bg-[#1a1d2e] border border-[#2d3748] rounded px-3 py-2 text-sm text-[#e2e8f0] mt-1" />
          </div>
          <div>
            <label className="text-xs text-[#7c8db5]">API Key</label>
            <input value={llmApiKey} onChange={function(e) { setLlmApiKey(e.target.value); }}
              type="password" placeholder="sk-..."
              className="w-full bg-[#1a1d2e] border border-[#2d3748] rounded px-3 py-2 text-sm text-[#e2e8f0] mt-1" />
          </div>
          <button onClick={handleSaveLlm} disabled={llmSaving}
            className="btn-primary flex items-center gap-1.5 text-sm px-4">
            {llmSaving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />} 保存 LLM 配置
          </button>
          {llmStatus && <p className="text-xs text-[#7c8db5]">{llmStatus}</p>}
        </div>
      </div>
    </div>
  );
}
