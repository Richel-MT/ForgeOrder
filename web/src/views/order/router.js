import Index from './Index.vue'
import Create from './Create.vue'


export default {
    path: '/order',
    component: Index,
    children: [
        {
            path: '/order/new',
            component: Create,
            meta: {
                title: '$order.title.create'
            }
        }
    ]
}