import React, { useState } from 'react';
import { Download, Image, FileText, Printer, Eye } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface QRCodeDownloadProps {
  qrCodeId: string;
  tenantId: string;
  qrCodeUrl: string;
}

type ModuleStyle = 'square' | 'rounded' | 'circle';

export const QRCodeDownload: React.FC<QRCodeDownloadProps> = ({
  qrCodeId,
  tenantId,
  qrCodeUrl,
}) => {
  const [size, setSize] = useState(300);
  const [style, setStyle] = useState<ModuleStyle>('square');
  const [color, setColor] = useState('#000000');
  const [bgColor, setBgColor] = useState('#FFFFFF');
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePreview = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        size: size.toString(),
        style,
        color: color.replace('#', ''),
        bg_color: bgColor.replace('#', ''),
      });

      const response = await apiClient.get(
        `/tenants/${tenantId}/qr-codes/${qrCodeId}/preview?${params}`,
        { responseType: 'json' }
      );

      setPreviewUrl(`data:image/png;base64,${response.data.image_base64}`);
    } catch (error) {
      console.error('Failed to generate preview:', error);
      alert('プレビューの生成に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPNG = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        size: size.toString(),
        style,
        color: color.replace('#', ''),
        bg_color: bgColor.replace('#', ''),
      });

      const response = await apiClient.get(
        `/tenants/${tenantId}/qr-codes/${qrCodeId}/download/png?${params}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `qrcode-${qrCodeId}.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PNG:', error);
      alert('PNGダウンロードに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadSVG = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        color: color.replace('#', ''),
        bg_color: bgColor.replace('#', ''),
      });

      const response = await apiClient.get(
        `/tenants/${tenantId}/qr-codes/${qrCodeId}/download/svg?${params}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `qrcode-${qrCodeId}.svg`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download SVG:', error);
      alert('SVGダウンロードに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPrintTemplate = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        size: size.toString(),
        style,
        color: color.replace('#', ''),
        bg_color: bgColor.replace('#', ''),
        title: 'DiagnoLeads診断',
        description: 'スマートフォンで読み取ってください',
      });

      const response = await apiClient.get(
        `/tenants/${tenantId}/qr-codes/${qrCodeId}/download/print?${params}`,
        { responseType: 'blob' }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `qrcode-print-${qrCodeId}.png`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download print template:', error);
      alert('印刷テンプレートのダウンロードに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">QRコード画像のダウンロード</h3>

      {/* Preview */}
      <div className="mb-6 flex justify-center">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 bg-gray-50">
          {previewUrl ? (
            <img src={previewUrl} alt="QR Code Preview" className="max-w-xs" />
          ) : (
            <div className="w-64 h-64 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <Image size={48} className="mx-auto mb-2" />
                <p className="text-sm">プレビューを生成してください</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Customization Options */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            サイズ (px)
          </label>
          <input
            type="range"
            min="200"
            max="1000"
            step="50"
            value={size}
            onChange={(e) => setSize(Number(e.target.value))}
            className="w-full"
          />
          <div className="text-center text-sm text-gray-600 mt-1">{size}px</div>
        </div>

        {/* Style */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            モジュールスタイル
          </label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value as ModuleStyle)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="square">四角</option>
            <option value="rounded">角丸</option>
            <option value="circle">円形</option>
          </select>
        </div>

        {/* Foreground Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            前景色
          </label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="h-10 w-20 rounded border border-gray-300"
            />
            <input
              type="text"
              value={color}
              onChange={(e) => setColor(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>

        {/* Background Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            背景色
          </label>
          <div className="flex items-center gap-2">
            <input
              type="color"
              value={bgColor}
              onChange={(e) => setBgColor(e.target.value)}
              className="h-10 w-20 rounded border border-gray-300"
            />
            <input
              type="text"
              value={bgColor}
              onChange={(e) => setBgColor(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={handlePreview}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <Eye size={18} />
          プレビュー
        </button>

        <button
          onClick={handleDownloadPNG}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <Download size={18} />
          PNG ダウンロード
        </button>

        <button
          onClick={handleDownloadSVG}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          <FileText size={18} />
          SVG ダウンロード
        </button>

        <button
          onClick={handleDownloadPrintTemplate}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          <Printer size={18} />
          印刷用テンプレート
        </button>
      </div>

      {/* Info */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>QR URL:</strong> {qrCodeUrl}
        </p>
      </div>
    </div>
  );
};
