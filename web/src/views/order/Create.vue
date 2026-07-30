<template>
    
   <BasicInfo v-if="index == 0" v-model:index ="index" v-model:orderInfo="orderBasicInfo"/>
   <Dishes v-if="index == 1" v-model:index ="index" />
   

</template> 


<script setup>
    import '@/assets/transition.css'
    import { ref, watch, defineAsyncComponent } from 'vue'

    const BasicInfo = defineAsyncComponent(
  () => import('@/views/order/components/CreateBasicInfo.vue')
)

    const Dishes = defineAsyncComponent(
  () => import('@/views/order/components/CreateDishes.vue')
)

    const index= ref(0)
    const currentComponent = ref(BasicInfo)

    const orderBasicInfo = ref({})

    const nextPage = () => {
        index.value++
    }

    watch(
        () => index.value,
        (newVal, oldVal) => {
            if (newVal == 0)  {
                currentComponent.value = BasicInfo
            }

        }
    )


    
</script>

<style>
    /* .bottom-bar {
        position:   ;
    } */

</style>