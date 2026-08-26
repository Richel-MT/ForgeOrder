<template>
    <div>
        <div class="container mdui-prose">
            <div v-if="isLoading" class="loading-container">
                <mdui-circular-progress></mdui-circular-progress>
            </div>
            <div v-else>
                <h2>订单 {{ orderInfo.displayCode }}</h2>

                <p class="order-id">唯一标识符：{{ id }}</p>
                
                <mdui-linear-progress :value="orderStatus" max="4"></mdui-linear-progress>
                
                <div class="state-container">
                    <div class="state-item">
                        已下单
                        {{ String(createdAt?.getHours()).padStart(2, '0') }}:{{ String(createdAt?.getMinutes()).padStart(2, '0') }}
                    </div>
                    <div class="state-item">制作中
                        <span v-if="orderStatus == 2">
                            {{ String(updatedAt?.getHours()).padStart(2, '0') }}:{{ String(updatedAt?.getMinutes()).padStart(2, '0') }}
                        </span>
                    </div>
                    <div class="state-item">待结账
                        <span v-if="orderStatus == 3">
                            {{ String(updatedAt?.getHours()).padStart(2, '0') }}:{{ String(updatedAt?.getMinutes()).padStart(2, '0') }}
                        </span>
                    </div>
                    <div class="state-item">
                        已结账
                        <span v-if="payAt !== null">
                            {{ String(payAt?.getHours()).padStart(2, '0') }}:{{ String(payAt?.getMinutes()).padStart(2, '0') }}
                        </span>
                        <!-- <span v-else>未结账</span> -->
                    </div>
                </div>



            </div>
            
            
        </div>
    </div>
</template>

<script setup>
    import { alert } from 'mdui/functions/alert.js'

    import { ref, onMounted } from 'vue'
    import request from '@/utils/request.js'
    
    import { useRouter } from 'vue-router'

    const props = defineProps({
        id: {
            type: String,
            default: ''
        }
    })


    const router = useRouter()

    const isLoading = ref(true)

    const orderInfo = ref({})

    const orderStatus = ref(0)

    const createdAt = ref(null)
    const payAt = ref(null)
    const updatedAt = ref(null)

    const fetchData = async () => {
        const res = await request.post("/order/get", {
            id: props.id,
            queries: ["basicInfo"]
        })

        if (res.data.status == 0) {
            orderInfo.value = res.data.data.result.basicInfo
            
            createdAt.value = new Date(orderInfo.value.createdAt)
            updatedAt.value = new Date(orderInfo.value.updatedAt)
            if (orderInfo.value.payAt !== null) {
                payAt.value = new Date(orderInfo.value.payAt)
            }

            orderStatus.value = orderInfo.value.status + 1
        
        
        


        } else if (res.data.status == 3002) {
            // 找不到订单
            alert({
                headline: "找不到订单",
                description: `订单“${props.id}”不存在。`,
                confirmText: "确定",
                onConfirm: () => router.psuh("/?index=1"),
            })
        }

        isLoading.value = false
    }

    onMounted(() => {
        fetchData()
    })
</script>

<style scoped>
    .loading-container {
        width: 100%;
        height: calc(100vh - 64px - 24px);
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .state-container {
        display: flex;
    }

    .state-item {
        flex: 1;
        text-align: right;
        font-size: 12px
    }

    h2 {
        margin-bottom: 12px;
    }

    .order-id {
        font-size: 12px
    }


    
</style>
