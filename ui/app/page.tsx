"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Loader2, CheckCircle, XCircle, FileText, Download, Play, Activity } from "lucide-react";

// API 基础地址
const API_BASE = "http://localhost:8000/api";

export default function Home() {
  const [topic, setTopic] = useState("polyp segmentation");
  const [depth, setDepth] = useState("light");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState("IDLE"); // IDLE, RUNNING, DONE, FAILED
  const [timeline, setTimeline] = useState<any[]>([]);
  const [reportMd, setReportMd] = useState("");
  const [loading, setLoading] = useState(false);

  // 轮询钩子
  useEffect(() => {
    if (!taskId || status === "DONE" || status === "FAILED") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/task/${taskId}`);
        const data = await res.json();
        
        setStatus(data.info.status);
        setTimeline(data.timeline);

        // 如果任务完成，尝试提取报告内容（这里简化处理，假设最后一步有报告文本）
        // 实际上我们可能需要一个新的 API 专门拉取 Markdown 文本
        // 这里做一个 hack：如果 DONE，显示下载链接即可，或者让后端把 MD 放在 tasks 表里
        if (data.info.status === "DONE") {
           // 触发一次文件下载或预览（下一阶段优化）
           fetchReportContent(taskId);
        }
      } catch (e) {
        console.error("Poll error:", e);
      }
    }, 2000); // 2秒轮询一次

    return () => clearInterval(interval);
  }, [taskId, status]);

  // 模拟获取报告内容（实际项目中可以加一个 API /task/{id}/content）
  const fetchReportContent = async (tid: string) => {
    // 暂时先只显示完成状态，真正的 Markdown 预览需要后端支持读取文件
    // 为了演示，我们在前端硬编码或通过 artifact 接口读取（如果是文本流）
    // 这里暂时留空，重点展示 Timeline 和 PDF 下载
    setReportMd(`## 报告已生成 \n\n 请点击右上方按钮下载 PDF 查看完整图表与引用。`);
  };

  const submitTask = async () => {
    setLoading(true);
    setTimeline([]);
    setStatus("RUNNING");
    setReportMd("");
    
    try {
      const res = await fetch(`${API_BASE}/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, depth }),
      });
      const data = await res.json();
      setTaskId(data.task_id);
    } catch (e) {
      alert("提交失败");
      setStatus("IDLE");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-blue-700 flex items-center justify-center gap-2">
            <Activity /> Medical AI TechRadar
          </h1>
          <p className="text-gray-500">Agentic RAG System for Medical Research</p>
        </header>

        {/* Input Area */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 space-y-4">
          <div className="flex gap-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="输入医学主题，例如：Lung Nodule Detection..."
            />
            <select
              value={depth}
              onChange={(e) => setDepth(e.target.value)}
              className="px-4 py-2 border rounded-lg bg-gray-50"
            >
              <option value="light">Light (快速)</option>
              <option value="deep">Deep (深度)</option>
            </select>
            <button
              onClick={submitTask}
              disabled={loading || status === "RUNNING"}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Play size={18} />}
              Start Agent
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Left: Timeline */}
          <div className="md:col-span-1 bg-white p-6 rounded-xl shadow-sm border border-gray-200 h-fit">
            <h3 className="font-semibold mb-4 text-gray-700">执行轨迹 (Timeline)</h3>
            <div className="space-y-4">
               {timeline.length === 0 && <p className="text-gray-400 text-sm">暂无记录...</p>}
               {timeline.map((step, idx) => (
                 <div key={idx} className="relative pl-6 border-l-2 border-gray-200 pb-2">
                    <div className="absolute -left-[9px] top-0 bg-white">
                      <CheckCircle size={16} className="text-green-500" />
                    </div>
                    <div className="text-sm font-medium text-gray-800">{step.step_name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(step.created_at).toLocaleTimeString()}
                    </div>
                 </div>
               ))}
               {status === "RUNNING" && (
                 <div className="relative pl-6 border-l-2 border-gray-200">
                    <div className="absolute -left-[9px] top-0 bg-white">
                      <Loader2 size={16} className="animate-spin text-blue-500" />
                    </div>
                    <div className="text-sm text-gray-500">Processing...</div>
                 </div>
               )}
            </div>
          </div>

          {/* Right: Report Preview */}
          <div className="md:col-span-2 bg-white p-8 rounded-xl shadow-sm border border-gray-200 min-h-[500px]">
            <div className="flex justify-between items-center mb-6 border-b pb-4">
              <h3 className="font-semibold text-gray-700 flex items-center gap-2">
                <FileText size={20} /> 报告预览
              </h3>
              {status === "DONE" && taskId && (
                <a
                  href={`${API_BASE}/artifact/${taskId}`}
                  target="_blank"
                  className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <Download size={16} /> 下载 PDF
                </a>
              )}
            </div>
            
            <article className="prose prose-sm max-w-none text-gray-800">
              {reportMd ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{reportMd}</ReactMarkdown>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                  <Activity size={48} className="mb-4 opacity-20" />
                  <p>等待任务完成生成报告...</p>
                </div>
              )}
            </article>
          </div>
        </div>
      </div>
    </div>
  );
}