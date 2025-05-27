        .low-score {{ color: #e74c3c; }}
        .recommendation {{
            font-size: 18px;
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
        }}
        .details {{
            margin-top: 15px;
        }}
        .detail-item {{
            margin: 5px 0;
            padding: 5px;
            background: #f8f9fa;
            border-radius: 3px;
        }}
        .value-estimate {{
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
        }}
        .btn {{
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px;
            transition: background 0.3s;
        }}
        .btn:hover {{
            background: #5a6fd8;
        }}
        .last-update {{
            text-align: center;
            color: white;
            margin-top: 40px;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔍 过期域名AI分析报告</h1>
            <p>基于人工智能的域名价值评估结果</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_domains}</div>
                <div class="stat-label">扫描域名总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{high_value_domains}</div>
                <div class="stat-label">高价值域名</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{recommended_domains}</div>
                <div class="stat-label">推荐域名</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_score}</div>
                <div class="stat-label">平均评分</div>
            </div>
        </div>

        <div class="content-section">
            <h2 class="section-title">🏆 高价值域名推荐</h2>
"""

        # 显示前20个高分域名
        top_domains = analyzed_domains[:20]
        
        for domain in top_domains:
            score_class = "high-score" if domain['total_score'] >= 80 else "medium-score" if domain['total_score'] >= 60 else "low-score"
            
            html_content += f"""
            <div class="domain-card">
                <div class="domain-name">{domain['domain']}</div>
                <div class="score {score_class}">综合评分: {domain['total_score']}/100</div>
                <div class="recommendation">{domain['recommendation']}</div>
                <div class="value-estimate">预估价值: {domain['estimated_value']}</div>
                <div class="details">
                    <strong>分析详情:</strong>
"""
            
            for detail in domain['analysis_details']:
                html_content += f'<div class="detail-item">{detail}</div>'
            
            html_content += """
                </div>
            </div>
"""

        html_content += f"""
        </div>

        <div class="content-section">
            <h2 class="section-title">📊 评分分布</h2>
            <p>本次扫描共分析了 {total_domains} 个域名，其中：</p>
            <ul style="margin: 20px 0; line-height: 2;">
                <li>🌟 <strong>高价值域名</strong> (80分以上): {high_value_domains} 个</li>
                <li>⭐ <strong>推荐域名</strong> (65-79分): {recommended_domains - high_value_domains} 个</li>
                <li>👀 <strong>中等价值</strong> (50-64分): {len([d for d in analyzed_domains if 50 <= d['total_score'] < 65])} 个</li>
                <li>⚠️ <strong>低价值域名</strong> (50分以下): {len([d for d in analyzed_domains if d['total_score'] < 50])} 个</li>
            </ul>
        </div>

        <div class="content-section">
            <h2 class="section-title">📋 分析说明</h2>
            <p>我们的AI分析系统从以下维度评估域名价值：</p>
            <ul style="margin: 20px 0; line-height: 2;">
                <li><strong>域名质量 (15%)</strong>: 长度、可读性、记忆性</li>
                <li><strong>关键词价值 (25%)</strong>: 包含的高价值关键词</li>
                <li><strong>品牌价值 (20%)</strong>: 品牌构建潜力</li>
                <li><strong>SEO潜力 (20%)</strong>: 搜索引擎优化价值</li>
                <li><strong>技术指标 (15%)</strong>: 域名年龄、反向链接等</li>
                <li><strong>商业价值 (5%)</strong>: 商业化潜力</li>
            </ul>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://github.com/a220ca/expired-domain-scanner" class="btn">📖 查看源码</a>
                <a href="https://github.com/a220ca/expired-domain-scanner/actions" class="btn">🔄 查看运行状态</a>
            </div>
        </div>

        <div class="last-update">
            <p><strong>扫描时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><small>💡 系统每日自动更新 | 🤖 AI驱动分析</small></p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ HTML报告已生成: {output_file}")


def main():
    """主函数"""
    print("🔍 启动过期域名AI分析系统...")
    print("=" * 50)
    
    try:
        # 初始化扫描器
        scanner = ExpiredDomainScanner()
        
        # 扫描域名
        print("📡 开始扫描域名...")
        domains = scanner.scrape_domain_list(max_pages=3)
        
        if not domains:
            print("❌ 未能获取到域名数据")
            return
        
        print(f"✅ 成功获取 {len(domains)} 个域名")
        
        # AI分析
        print("🧠 开始AI价值分析...")
        analyzed_domains = scanner.analyze_domains(domains)
        
        # 保存结果
        print("💾 保存分析结果...")
        files = scanner.save_results(analyzed_domains)
        
        # 显示摘要
        print("\n" + "=" * 50)
        print("📊 扫描完成摘要:")
        print(f"   • 总域名数: {len(analyzed_domains)}")
        print(f"   • 高价值域名: {len([d for d in analyzed_domains if d['total_score'] >= 80])}")
        print(f"   • 推荐域名: {len([d for d in analyzed_domains if d['total_score'] >= 65])}")
        print(f"   • 平均评分: {round(sum(d['total_score'] for d in analyzed_domains) / len(analyzed_domains), 1)}")
        
        print("\n🏆 Top 5 推荐域名:")
        for i, domain in enumerate(analyzed_domains[:5], 1):
            print(f"   {i}. {domain['domain']} - {domain['total_score']}分 - {domain['estimated_value']}")
        
        print(f"\n📄 详细报告: {files.get('html', 'N/A')}")
        print("🎉 分析完成！")
        
    except Exception as e:
        print(f"❌ 系统运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
