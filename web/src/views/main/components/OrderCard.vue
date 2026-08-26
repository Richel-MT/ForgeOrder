<template>
    <div class="card-container" ref="containerRef">
            <mdui-card class="order-card" variant="outlined" clickable @click="router.push(`/order/${props.orderId}`)">
                <!-- 顶部信息-->
                <div class="card-header">
                    <div class="header-left">

                        <div>
                            <!-- <span class="header-left-item-key"></span> -->
                            <span class="header-left-item-value">{{ displayCode }}</span>
                        </div>

                        <div>
                            <span class="header-left-item-value">
                                {{ orderType == 0 ? '堂食' : '外带' }}
                            </span>
                        </div>

                        <div v-if="orderType == 0">
                            <span class="header-left-item-key">桌台</span>
                            <span class="header-left-item-value">{{ tableName }}</span>
                        </div>
                        <div v-if="orderType == 0">
                            <span class="header-left-item-key">人数</span>
                            <span class="header-left-item-value">{{ partySize }}</span>
                        </div>
                        
                    </div>

                    <div class="header-right">{{  state  }}</div>
                </div>

                <!--进度信息-->
                <div class="progress-content">
                    <div class="progress-label">订单:
                        <span v-if="finishedSubOrders != -1 && totalSubOrders != -1">{{ finishedSubOrders }}/{{ totalSubOrders }}</span>
                        <span v-else>加载中</span>
                    </div>
                    <mdui-linear-progress :value=" finishedSubOrders != -1 ? finishedSubOrders : undefined" :max="totalSubOrders != -1 ? totalSubOrders : undefined" class="progress-bar"></mdui-linear-progress>
                </div>
            
                <!--进度信息-->
                <div class="progress-content">
                    <div class="progress-label">菜品:
                        <span v-if="finishedDishes != -1 && totalSubOrders != -1">{{ finishedDishes }}/{{ totalDishes }}</span>
                        <span v-else>加载中</span>
                    </div>
                    <mdui-linear-progress :value="finishedDishes != -1 ? finishedDishes : undefined" :max="totalDishes != -1 ? totalDishes : undefined" class="progress-bar"></mdui-linear-progress>
                </div>

                <!-- 底部信息-->
                <div class="footer-content">
                    <div>
                        <span class="footer-item">{{ formatDateInTime(createTime) }}</span>
                        （已等{{ waitTime }}）
                    </div>
                    <div class="footer-item">
                        ￥ {{ (totalPrice / 100).toFixed(2) }}
                    </div>
                </div>

                
            </mdui-card>
            <!--操作区域-->
        </div>

</template> 

<script setup>
    import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
    import { useIntersectionObserver } from '@vueuse/core'

    import 'mdui/components/card.js';
    import 'mdui/components/fab.js';
    import 'mdui/components/linear-progress.js';
    import 'mdui/components/divider.js';
    import 'mdui/components/button-icon.js';

    import '@mdui/icons/done-outline.js';
    import '@mdui/icons/payment.js';
    import '@mdui/icons/print.js';
    import '@mdui/icons/more-vert.js';
    import '@mdui/icons/edit.js';

    import { formatDateInTime, getSub } from '@/utils/date.js';

    import { useRouter } from 'vue-router';

    import request from '@/utils/request.js'
;
    const router = useRouter();

    const props = defineProps({
        orderId: {  // 订单在系统内的唯一id
            type: String,
            default: 0
        },
        tableId: { // 桌号
            type: Number
        },
        partySize: {  // 人数
            type: Number,
            default: 0
        },
        status: { // 状态
            type: Number,
            default: 0
        },
        orderType: { // 订单类型(0: 堂食, 1: 外带)
            type: Number,
            default: 0
        },
        createTime: { // 创建时间
            type: Date,
            default: new Date()
        },
        totalPrice: { // 总金额（单位：分）
            type: Number,
            default: 0
        },
        displayCode: {
            type: Number,
            default: -1
        }
    })


    const state = computed(() => {
        if (props.status === 0) {
            return '已下单'
        } else if (props.status === 1) {
            return '制作中'
        } else if (props.status === 2) {
            return '待结账'
        } else if (props.status === 3) {
            return '已结账'
        }
        
    })

    const waitTime = computed(() => {
        const waitTime = getSub(new Date(), props.createTime)
        
        if (waitTime.hour > 0) {
            return `${waitTime.hour}小时${waitTime.minute}分钟`
        } else if (waitTime.minute > 0) {
            return `${waitTime.minute}分钟`
        } else {
            return `${waitTime.second}秒`
        }
    })

    const finishedSubOrders = ref(-1)
    const totalSubOrders = ref(-1)

    const finishedDishes = ref(-1)
    const totalDishes = ref(-1)

    const tableName = ref('加载中')

    const isLoading = ref(false)

    const isLoaded = ref(false)

    const containerRef= ref(null)

    const fetchData =  async () => {
        if (isLoading.value || isLoaded.value) return 

        isLoading.value = true

        const queries = ["subOrdersCount", "dishesCount"]

        if (props.orderType == 0) {
            queries.push("tableName")
        }
        try {
            const res = await request.post("/order/get", {
                "id": props.orderId,
                "queries": queries
            })

            finishedSubOrders.value = res.data.data.result?.subOrdersCount.finished
            totalSubOrders.value = res.data.data.result?.subOrdersCount.total

            finishedDishes.value = res.data.data.result?.dishesCount.finished
            totalDishes.value = res.data.data.result?.dishesCount.total

            tableName.value = res.data.data.result?.tableName

            isLoaded.value = true
        } catch (error) {
            console.error("加载失败", error)
        } finally {
            isLoading.value = false
        }
        
    }

    const { stop } = useIntersectionObserver(
        containerRef,
        ([{ isIntersecting }]) => {
            if (isIntersecting && !isLoaded.value && !isLoading.value) {
                fetchData()
            }
        },
        {
            threshold: 0.5
        }
    )

    onBeforeUnmount(() => {
        stop()
    })




</script>

<style>
    .container .card-container {
        margin-bottom: 24px ;
    }

    .order-card {
        width: 100%;  
        padding: 12px; 
        margin-bottom: 0
    }
    
    .card-header {
        display: flex; 
        justify-content: space-between; 
        align-items: center;
    }

    .header-left {
        display: flex;
        gap:8px
    }

    .header-left-item-key {
        margin-right: 5px;
        font-size: 12px
    }

    .header-left-item-value {
        font-size: 20px;
    }

    .header-right {
        text-align: right;
         font-size: 20px;
    }

    .progress-content {
        display: flex;
         align-items: center;
    }

    .progress-label {
        font-size: 14px;
         flex-shrink: 0;
          white-space: nowrap;
           margin-right: 8px
    }

    .progress-bar {
        flex: 1;
    }

    .unfinished-dishes {
        font-size: 14px;
    }


    .footer-content {
        display: flex;
        justify-content: space-between;
    }

    .footer-item {
        font-size: 20px;
    }

    .action-content {
        display: flex; 
        justify-content: flex-end;
    }


</style>