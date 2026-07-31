<template>
    <div class="number-select">
        <mdui-button-icon    @click="removeNumber"><mdui-icon-remove></mdui-icon-remove></mdui-button-icon>
        {{ props.modelValue }}
        <mdui-button-icon    @click="addNumber"><mdui-icon-add></mdui-icon-add></mdui-button-icon>       
    </div>
</template>

<script setup>
    import '@mdui/icons/add.js';
    import '@mdui/icons/remove.js';

    const props = defineProps({
        modelValue: {
            type: Number,
            default: 0
        },
        onChanged: {
            type: Function,
            default: () => {}
        }
    })

    const emit = defineEmits(['update:modelValue'])

    const addNumber = () => {
        let result = props.onChanged(props.modelValue, props.modelValue + 1)
        if (result) {
            emit('update:modelValue', props.modelValue + 1)
        } else {
            // console.log("false", result)
        }
    }
    const removeNumber = () => {
        if (props.onChanged(props.modelValue, props.modelValue - 1)) {
            emit('update:modelValue', props.modelValue - 1)
        }
    }

</script>

<style>
 .number-select {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px
 }
</style>