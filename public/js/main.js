// 页面加载时获取产品列表
document.addEventListener('DOMContentLoaded', () => {
    fetchProducts();

    // 添加产品表单提交
    const form = document.getElementById('add-product-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const price = parseFloat(document.getElementById('price').value);
        const stock = parseInt(document.getElementById('stock').value);

        try {
            const response = await fetch('/api/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, price, stock })
            });
            if (response.ok) {
                // 清空表单
                form.reset();
                // 重新加载产品列表
                fetchProducts();
            } else {
                alert('添加失败');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('网络错误');
        }
    });
});

async function fetchProducts() {
    try {
        const response = await fetch('/api/products');
        const products = await response.json();
        renderProducts(products);
    } catch (error) {
        console.error('Error fetching products:', error);
        document.getElementById('product-list').innerHTML = '<p>加载产品列表失败</p>';
    }
}

function renderProducts(products) {
    const container = document.getElementById('product-list');
    if (products.length === 0) {
        container.innerHTML = '<p>暂无产品，请添加。</p>';
        return;
    }
    container.innerHTML = products.map(product => `
        <div class="product-item">
            <h3>${escapeHtml(product.name)}</h3>
            <p>价格：¥${product.price.toFixed(2)}</p>
            <p>库存：${product.stock}</p>
        </div>
    `).join('');
}

// 简单的防XSS辅助函数
function escapeHtml(str) {
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}