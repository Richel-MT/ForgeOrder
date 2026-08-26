import Index from './Index.vue'
import Create from './Create.vue'
import OrderDetail from './OrderDetail.vue'

export default {
    path: '/order',
    component: Index,
    children: [
        {
            path: 'new',
            component: Create,
            meta: {
                title: '$order.title.create'
            }
        },
        {
            path: ':id',
            component: OrderDetail,
            meta: {
                title: '订单详情'
            },
            props: true
        }
    ]
}