import Vue from 'vue'

import VueRouter from 'vue-router'

Vue.use(VueRouter)

import VueResource from 'vue-resource';

Vue.use(VueResource);

import App from './App.vue'
import Login from './components/login.vue';
import Register from './components/register.vue';


const AddStudyroom = require('./components/add-studyrooms.vue');
const EditStudyroom = require('./components/edit-studyroom.vue');
const AllStudyrooms = require('./components/all-studyrooms.vue');
const IBookingIndex = require('./components/ibooking-index.vue');
const AllSeats = require('./components/all-seats.vue');
const AddSeat = require('./components/add-seats.vue');
const EditSeat = require('./components/edit-seat.vue');
const IBookingAllSeats = require('./components/ibooking-all-seats.vue');
const IBookingAllSeatBookings = require('./components/ibooking-all-seat-bookings.vue');
const IBookingAllUserBookings = require('./components/ibooking-all-user-bookings.vue');

const routes = [
    {
        name: 'login',
        path: '/',
        component: Login
    },
    {
        name: 'login',
        path: '/login',
        component: Login
    },
    {
        name: 'register',
        path: '/register',
        component: Register
    },
    {
        name: 'all_studyrooms',
        path: '/all_studyrooms',
        component: AllStudyrooms,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'add_studyroom',
        path: '/studyroom/add_studyroom',
        component: AddStudyroom,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'edit_studyroom',
        path: '/studyroom/edit/:studyroom',
        component: EditStudyroom,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'all_seats',
        path: '/all_seats',
        component: AllSeats,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'add_seat',
        path: '/seat/add_seat',
        component: AddSeat,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'edit_seat',
        path: '/seat/edit_seat',
        component: EditSeat,
        meta: {requiresAuth: true, requiresRole: '1'}
    },
    {
        name: 'ibooking_index',
        path: '/ibooking_index',
        component: IBookingIndex,
        meta: {requiresAuth: true}
    },
    {
        name: 'ibooking_all_seats',
        path: '/ibooking_all_seats',
        component: IBookingAllSeats,
        meta: {requiresAuth: true}
    },
    {
        name: 'ibooking_all_seat_bookings',
        path: '/ibooking_all_seat_bookings',
        component: IBookingAllSeatBookings,
        meta: {requiresAuth: true}
    },
    {
        name: 'ibooking_all_user_bookings',
        path: '/ibooking_all_user_bookings',
        component: IBookingAllUserBookings,
        meta: {requiresAuth: true}
    }
];

const router = new VueRouter({routes: routes, mode: 'history'});

// 路由守卫，检查是否登录
router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.requiresAuth)) {
        // 如果需要登录，检查是否已经登录
        if (!localStorage.getItem('userId')) {
            next({name: 'login'}); // 如果未登录，跳转到登录页面
        } else {
            const userRole = localStorage.getItem('userRole'); // 获取用户角色
            // 检查角色权限（如果有角色限制）
            if (to.meta.requiresRole && to.meta.requiresRole !== userRole) {
                alert('您没有权限访问此页面');
                next({name: 'ibooking_index'}); // 普通用户试图访问管理页面时，自动跳转到 ibooking_index 页面
            } else {
                next(); // 允许访问
            }
        }
    } else {
        next(); // 如果不需要登录，继续访问
    }
});

new Vue(Vue.util.extend({router}, App)).$mount('#app');