// 全局配置
const API_URL = 'http://localhost:5000/api';

// DOM元素
const navLinks = document.querySelectorAll('nav a');
const sections = document.querySelectorAll('main section');
const categoryFilter = document.getElementById('category-filter');
const searchInput = document.getElementById('search-input');
const conceptsContainer = document.getElementById('concepts-container');
const graphContainer = document.getElementById('graph-container');
const graphStats = document.getElementById('graph-stats');
const modal = document.getElementById('concept-detail-modal');
const conceptDetailContainer = document.getElementById('concept-detail-container');
const closeButton = document.querySelector('.close-button');

// 导航切换
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        
        // 更新导航链接状态
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        
        // 更新内容区域
        const targetId = this.id.replace('nav-', '');
        sections.forEach(section => {
            section.classList.remove('active');
            if (section.id === targetId) {
                section.classList.add('active');
                
                // 加载相应内容
                if (section.id === 'concepts' && conceptsContainer.childElementCount <= 1) {
                    loadCategories();
                    loadConcepts();
                } else if (section.id === 'graph' && !graphContainer.hasChildNodes()) {
                    initGraph();
                }
            }
        });
    });
});

// 加载分类数据
async function loadCategories() {
    try {
        const response = await fetch(`${API_URL}/categories`);
        const categories = await response.json();
        
        if (Array.isArray(categories)) {
            // 清空现有选项（保留"全部"）
            categoryFilter.innerHTML = '<option value="">全部类别</option>';
            
            // 添加类别选项
            categories.forEach(category => {
                if (category) {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categoryFilter.appendChild(option);
                }
            });
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 加载概念数据
async function loadConcepts(category = '') {
    try {
        let url = `${API_URL}/concepts`;
        if (category) {
            url += `?category=${encodeURIComponent(category)}`;
        }
        
        conceptsContainer.innerHTML = '<p>正在加载概念数据...</p>';
        
        const response = await fetch(url);
        const concepts = await response.json();
        
        if (Array.isArray(concepts)) {
            // 更新图谱统计
            updateGraphStats(concepts);
            
            // 渲染概念卡片
            conceptsContainer.innerHTML = '';
            concepts.forEach(concept => {
                const card = document.createElement('div');
                card.className = 'concept-card';
                card.setAttribute('data-id', concept.id);
                
                card.innerHTML = `
                    <h3>${concept.name}</h3>
                    <p>${concept.description}</p>
                    <div class="category-tag">${concept.category || '未分类'}</div>
                `;
                
                card.addEventListener('click', () => showConceptDetail(concept.id));
                conceptsContainer.appendChild(card);
            });
            
            if (concepts.length === 0) {
                conceptsContainer.innerHTML = '<p>没有找到符合条件的概念</p>';
            }
        }
    } catch (error) {
        console.error('加载概念失败:', error);
        conceptsContainer.innerHTML = '<p>加载概念数据失败</p>';
    }
}

// 更新图谱统计
function updateGraphStats(concepts) {
    if (!Array.isArray(concepts) || concepts.length === 0) return;
    
    // 计算各类别的数量
    const categoryCounts = {};
    concepts.forEach(concept => {
        const category = concept.category || '未分类';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    // 更新统计显示
    graphStats.innerHTML = `
        <p>知识图谱包含 <strong>${concepts.length}</strong> 个概念</p>
        <p>概念类别统计:</p>
        <ul>
            ${Object.entries(categoryCounts)
                .map(([category, count]) => `<li>${category}: ${count}个</li>`)
                .join('')}
        </ul>
    `;
}

// 显示概念详情
async function showConceptDetail(conceptId) {
    try {
        modal.style.display = 'block';
        conceptDetailContainer.innerHTML = '<p>正在加载概念详情...</p>';
        
        const response = await fetch(`${API_URL}/concept/${conceptId}`);
        const concept = await response.json();
        
        if (concept.error) {
            conceptDetailContainer.innerHTML = `<p>错误: ${concept.error}</p>`;
            return;
        }
        
        let relationsHtml = '';
        if (concept.relations && concept.relations.length > 0) {
            relationsHtml = `
                <h3>相关概念</h3>
                <ul class="relations-list">
                    ${concept.relations.map(rel => `
                        <li>
                            <span class="relation-type">${rel.type}</span>
                            <a href="#" data-id="${rel.target_id}" class="related-concept">
                                ${rel.target_name} <span class="category-tag">${rel.target_category || '未分类'}</span>
                            </a>
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            relationsHtml = '<p>没有相关概念</p>';
        }
        
        conceptDetailContainer.innerHTML = `
            <h2>${concept.name}</h2>
            <div class="concept-meta">
                <div class="category-tag">${concept.category || '未分类'}</div>
            </div>
            <div class="concept-description">
                <p>${concept.description}</p>
            </div>
            <div class="concept-relations">
                ${relationsHtml}
            </div>
        `;
        
        // 为相关概念添加点击事件
        const relatedLinks = conceptDetailContainer.querySelectorAll('.related-concept');
        relatedLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('data-id');
                showConceptDetail(targetId);
            });
        });
    } catch (error) {
        console.error('加载概念详情失败:', error);
        conceptDetailContainer.innerHTML = '<p>加载概念详情失败</p>';
    }
}

// 初始化图谱可视化
function initGraph() {
    // 这里使用D3.js创建力导向图
    // 注意：这是一个简化版本，实际项目中可能需要更复杂的实现
    graphContainer.innerHTML = '<div class="loading">正在加载图谱数据...</div>';
    
    fetch(`${API_URL}/concepts`)
        .then(response => response.json())
        .then(concepts => {
            if (!Array.isArray(concepts) || concepts.length === 0) {
                graphContainer.innerHTML = '<p>没有可用的图谱数据</p>';
                return;
            }
            
            graphContainer.innerHTML = '';
            
            // 创建SVG容器
            const svg = d3.select('#graph-container')
                .append('svg')
                .attr('width', '100%')
                .attr('height', '100%');
            
            // 创建缩放功能
            const zoom = d3.zoom()
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {
                    container.attr('transform', event.transform);
                });
            
            svg.call(zoom);
            
            const container = svg.append('g');
            
            // 模拟关系数据
            const nodes = concepts.map(c => ({
                id: c.id,
                name: c.name,
                category: c.category || '未分类'
            }));
            
            // 简单地创建一些连接，实际中应该从API获取
            const links = [];
            for (let i = 0; i < Math.min(concepts.length, 20); i++) {
                const source = nodes[i];
                const target = nodes[Math.floor(Math.random() * nodes.length)];
                if (source.id !== target.id) {
                    links.push({ source: source.id, target: target.id });
                }
            }
            
            // 设置力导向图
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(
                    graphContainer.clientWidth / 2, 
                    graphContainer.clientHeight / 2
                ));
            
            // 绘制连接
            const link = container.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', 1);
            
            // 创建节点
            const node = container.append('g')
                .selectAll('g')
                .data(nodes)
                .enter().append('g')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended))
                .on('click', (event, d) => showConceptDetail(d.id));
            
            // 节点圆圈
            node.append('circle')
                .attr('r', 10)
                .attr('fill', d => categoryColor(d.category));
            
            // 节点文本
            node.append('text')
                .attr('dx', 12)
                .attr('dy', '.35em')
                .text(d => d.name);
            
            // 更新力导向图
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('transform', d => `translate(${d.x},${d.y})`);
            });
            
            // 拖拽功能
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
            
            // 为缩放按钮添加事件
            document.getElementById('zoom-in').addEventListener('click', () => {
                svg.transition()
                    .duration(300)
                    .call(zoom.scaleBy, 1.2);
            });
            
            document.getElementById('zoom-out').addEventListener('click', () => {
                svg.transition()
                    .duration(300)
                    .call(zoom.scaleBy, 0.8);
            });
            
            document.getElementById('reset-view').addEventListener('click', () => {
                svg.transition()
                    .duration(300)
                    .call(zoom.transform, d3.zoomIdentity);
            });
        })
        .catch(error => {
            console.error('加载图谱数据失败:', error);
            graphContainer.innerHTML = '<p>加载图谱数据失败</p>';
        });
}

// 根据类别返回颜色
function categoryColor(category) {
    const colors = {
        '核心概念': '#4299E1',
        '五位': '#48BB78',
        '色法': '#F6AD55',
        '心法': '#FC8181',
        '心所法': '#B794F4',
        '心不相应行法': '#9AE6B4',
        '无为法': '#FBD38D'
    };
    
    return colors[category] || '#CBD5E0';
}

// 关闭模态框
closeButton.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// 分类筛选
categoryFilter.addEventListener('change', () => {
    loadConcepts(categoryFilter.value);
});

// 搜索功能
searchInput.addEventListener('input', debounce(function() {
    const searchTerm = this.value.toLowerCase().trim();
    const cards = conceptsContainer.querySelectorAll('.concept-card');
    
    cards.forEach(card => {
        const name = card.querySelector('h3').textContent.toLowerCase();
        const description = card.querySelector('p').textContent.toLowerCase();
        
        if (name.includes(searchTerm) || description.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}, 300));

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 初始加载概览页的数据
    loadConcepts();
});