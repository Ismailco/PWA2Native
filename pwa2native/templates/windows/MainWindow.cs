using System;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace ${project_name}
{
    public class MainWindow : Form
    {
        private WebView2 webView;

        public MainWindow()
        {
            Title = "${app_name}";
            Size = new System.Drawing.Size(1024, 768);
            StartPosition = FormStartPosition.CenterScreen;

            InitializeWebView();
        }

        private async void InitializeWebView()
        {
            webView = new WebView2();
            webView.Dock = DockStyle.Fill;
            Controls.Add(webView);

            await webView.EnsureCoreWebView2Async(null);
            webView.CoreWebView2.Navigate("${url}");

            // Handle title changes
            webView.CoreWebView2.DocumentTitleChanged += (s, e) =>
            {
                this.Invoke((MethodInvoker)(() =>
                {
                    this.Text = webView.CoreWebView2.DocumentTitle;
                }));
            };
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            webView.Dispose();
            base.OnFormClosing(e);
        }
    }
}
