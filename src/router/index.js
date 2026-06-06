import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/dashboard',
    name: 'Layout',
    component: () => import('../components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: 'inventory'
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('../views/Inventory.vue')
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('../views/Sales.vue')
      },
      {
        path: 'purchase',
        name: 'Purchase',
        component: () => import('../views/Purchase.vue')
      },
      {
        path: 'suppliers',
        redirect: '/dashboard/purchase'
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue')
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('../views/Employee.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/Finance.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('../views/Stats.vue')
      },
      {
        path: 'return/:orderId',
        name: 'ReturnOrder',
        component: () => import('../views/ReturnOrder.vue')
      },
      {
        path: 'database',
        name: 'DataAdmin',
        component: () => import('../views/DatabaseAdmin.vue'),
        meta: { requiresAdmin: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  
  if (to.path === '/login') {
    if (token) {
      next('/dashboard/inventory');
    } else {
      next();
    }
  } else {
    if (!token || !user) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      next('/login');
      return;
    }
    
    try {
      const userData = JSON.parse(user);
      
      if (to.meta.requiresAdmin && userData.role !== 'admin') {
        next('/dashboard/inventory');
        return;
      }
      
      next();
    } catch (e) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      next('/login');
    }
  }
});

export default router;