import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '../stores/user';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
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
        redirect: '/purchase'
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue')
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('../views/Employee.vue')
      },
      {
        path: 'finance',
        name: 'Finance',
        component: () => import('../views/Finance.vue')
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
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  if (to.path === '/login') {
    if (userStore.isLoggedIn) {
      next('/inventory');
    } else {
      next();
    }
  } else {
    if (userStore.isLoggedIn) {
      next();
    } else {
      next('/login');
    }
  }
});

export default router;