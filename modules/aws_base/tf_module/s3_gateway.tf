resource "aws_vpc_endpoint" "s3" {
  vpc_id            = local.vpc_id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  tags = {
    Name      = "opta-${var.layer_name}-s3-gateway"
    terraform = "true"
  }
}

resource "aws_vpc_endpoint_route_table_association" "s3" {
  count           = local.create_vpc ? length(var.private_ipv4_cidr_blocks) : 0
  vpc_endpoint_id = aws_vpc_endpoint.s3.id
  route_table_id  = aws_route_table.private_route_tables[count.index].id
}